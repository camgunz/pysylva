import re

import llvmlite # type: ignore

from llvmlite import ir

# pylint: disable=unused-import
from . import ast, debug, errors
from .location import Location
from .module_builder import ModuleBuilder
from .parser import Lark_StandAlone as Parser


_IDENTIFIER_DELIMITERS = re.compile(r'(\.|::)')


class Module:

    def __init__(self, program, name, streams, requirement_statements):
        self._program = program
        self._name = name
        self._streams = streams
        self._requirement_statements = requirement_statements
        self._parsed = False
        self._trees = []
        self._errors = []
        self._llvm_module = None
        self._aliases = {}
        self._llvm_symbols = {}

        self.vars = {}
        self.vars.update(ast.BUILTIN_TYPES)
        self.requirements = set()
        self.type = ast.ModuleType(Location.Generate(), self)

    @property
    def name(self):
        return self._name

    @property
    def target(self):
        return self._program.target

    @property
    def llvm_module(self):
        return self._llvm_module

    def __repr__(self):
        return 'Module(%r, %r, %r, %r)' % (
            self._program,
            self._name,
            self._streams,
            self._requirement_statements
        )

    def __str__(self):
        return f'<Module {self.name}>'

    def resolve_requirements(self, seen=None):
        if len(self.requirements) == len(self._requirement_statements):
            return
        seen = seen or set()
        if self in seen:
            raise errors.CircularDependency(self, seen)
        seen.add(self)
        for requirement_statement in self._requirement_statements:
            module = self._program.get_module(requirement_statement.name)
            if not module:
                raise errors.NoSuchModule(
                    requirement_statement.location, requirement_statement.name
                )
            self.requirements.add(module)
            self.vars[module.name] = module
        for requirement in self.requirements:
            requirement.resolve_requirements(seen)

    def get_identified_type(self, name):
        return self._llvm_module.context.get_identified_type(name)

    def parse(self):
        if self._parsed:
            return self._errors

        for s in self._streams:
            ModuleBuilder(self, s).visit(Parser().parse(s.data))

        for name, obj in self.vars.items():
            if isinstance(obj, ast.SylvaType):
                self._errors.extend(obj.check())

            if isinstance(obj, ast.MetaSylvaType):
                self._errors.extend(obj.resolve_self_references(name))

        self._parsed = True

        return self._errors

    def _compile_expr(self, builder, expr, local_vars):
        debug('compile_expr', f'_compile_expr: {expr} {local_vars}')

        if isinstance(expr, ast.LiteralExpr):
            return expr.get_llvm_value(self)

        if isinstance(expr, ast.LookupExpr):
            # Might be:
            # - ConstDef
            # - FunctionDef
            # - CFunctionDef
            # - StructDef
            # - CStructDef
            # - InterfaceDef (TODO)
            # - EnumDef (TODO)
            # - VariantDef (TODO)
            # - Enum
            # - Variant
            # - CUnion
            # - Interface
            value = expr.eval(module, local_vars)

            res = local_vars.get(expr.name)

            if res is not None:
                value = res[1] # LLVM value
            else:
                value = self.lookup(expr.location, expr.name, local_vars)
                if value is not None:
                    value = self.get_or_define_llvm_symbol(expr.name, value)

            if not value:
                raise errors.UndefinedSymbol(expr.location, expr.name)

            return value

        if isinstance(expr, ast.FieldNameLookupExpr):
            # Might be:
            # - (Remote) ConstDef
            # - (Remote) FunctionDef
            # - (Remote) CFunctionDef
            # - (Remote) StructDef
            # - (Remote) CStructDef
            # - (Remote) InterfaceDef (TODO)
            # - (Remote) EnumDef (TODO)
            # - (Remote) VariantDef (TODO)
            # - Enum field
            # - Variant field
            # - CUnion field
            # - Interface function

            res = local_vars.get(expr.name)
            # value = builder.block.scope.get(expr.name)

            if res is not None:
                value = res[1] # LLVM value
            else:
                value = expr.object.lookup(expr.location, expr.name)
                if value is not None:
                    value = self.get_or_define_llvm_symbol(expr.name, value)

            if value is None:
                raise errors.NoSuchField(expr.location, expr.name)

            return value

        if isinstance(expr, ast.FieldIndexLookupExpr):
            return expr.emit(builder)
            indices = [expr.index]

            while isinstance(expr.object, ast.FieldIndexLookupExpr):
                expr = expr.object
                indices.insert(0, expr.index)

            return builder.gep(
                expr.object, # struct, cstruct
                indices,
                inbounds=True,
                name=expr.name
            )

        # if isinstance(expr, ast.ConstExpr):
        #     # This catches CVoidCast and MoveExpr... why?
        #     pass

        if isinstance(expr, ast.CallExpr):
            func = self._compile_expr(builder, expr.function, local_vars)
            args = [
                self._compile_expr(builder, arg_expr, local_vars)
                for arg_expr in expr.arguments
            ]

            return builder.call(func, [builder.load(arg) for arg in args])

        if isinstance(expr, ast.CPointerCastExpr):
            value = self._compile_expr(builder, expr.value, local_vars)
            if value.type.is_pointer:
                return value

            stack_slot = builder.alloca(value.type)
            builder.store(value, stack_slot)
            return stack_slot

        if isinstance(expr, ast.CVoidCastExpr):
            value = self._compile_expr(builder, expr.value, local_vars)
            return builder.bitcast(value, ir.IntType(8).as_pointer())

        if isinstance(expr, ast.ReflectionLookupExpr):
            # ReflectionLookupExpr
            # - type: i64
            # - object: LookupExpr
            #   - type: ReferencePointerType
            #     - referenced_type: StringType
            #   - name: message
            # - name: size
            #
            # Alright, the problem here is that this recursive algorithm
            # assumes everything returns LLVM objects, but in order to unwrap
            # this, I need to at least some times return Sylva objects.

            # object = eval(expr.object) # Runs the LookupExpr, gets the
            #                            # literal, etc. This means that
            #                            # expr.object is const
            # Get a reference pointer to a string
            # Base pointers are... also const? No, dereferencing them is. So
            # what we can do is do object.deref() if it's a BasePoniterExpr.
            # if isinstance(object, ast.BasePointerExpr):
            #     object = object.defer(location)
            # value = object.reflect(location, expr.name)

            value = expr.object
            value = self._compile_expr(builder, expr.object, local_vars)
            if not isinstance(value, ast.ValueExpr):
                import pdb
                pdb.set_trace()
                raise Exception('Non-value-expr stored as a value expr')
            return self._compile_expr(
                builder, value.reflect(expr.location, expr.name), local_vars
            )

        if isinstance(expr, ast.ValueExpr):
            # [TODO] Do the alloca

            # I can just look this up now
            res = local_vars.get(expr.name)

            if res is None:
                raise errors.UndefinedSymbol(expr.location, expr.name)

            return res[0] # Sylva value

        import pdb
        pdb.set_trace()

        raise NotImplementedError()

    # pylint: disable=too-many-locals
    def _compile_function(self, name, function_def):
        function = function_def.type
        llvm_func = self._llvm_module.get_global(name)
        block = llvm_func.append_basic_block()
        builder = ir.IRBuilder(block=block)
        params = function.parameters.items()
        local_vars = {}
        for arg, param_name_and_param_type in zip(llvm_func.args, params):
            # [FIXME] Parameters really need to be their own thing, with
            #         locations
            param_name, param_type = param_name_and_param_type
            # [TODO] Register the parameter types
            # I think what has to happen here is I need to run .get_value()
            # for each of the params.
            param_llvm_type = param_type.get_llvm_type(self)
            alloca = builder.alloca(param_llvm_type, name=param_name)
            builder.store(arg, alloca)
            # Maybe this is an object that stores the alloca? So then when I
            # look it up in local_vars I can switch on its type and pull it
            # out?
            local_vars[param_name] = alloca
        self._compile_code_block(function_def.code, builder, local_vars)

    def _compile_code_block(self, code, builder, local_vars):
        for node in code:
            if isinstance(node, ast.Expr):
                self._compile_expr(builder, node, local_vars)

    def _get_or_define_llvm_function_type(self, name, function_type):
        existing_function_type = self._llvm_symbols.get(name)
        if existing_function_type:
            return existing_function_type

        llvm_type = function_type.get_llvm_type(self)
        func = ir.Function(self._llvm_module, llvm_type, name)

        self._llvm_symbols[name] = func

        return func

    def _get_or_define_llvm_variable_type(self, name, variable_type):
        existing_variable_type = self._llvm_symbols.get(name)
        if existing_variable_type:
            return existing_variable_type

        llvm_type = variable_type.get_llvm_type(self)
        var = ir.GlobalVariable(self._llvm_module, llvm_type, name)

        self._llvm_symbols[name] = var

        return var

    def _get_or_define_llvm_constant(self, name, constant):
        existing_constant = self._llvm_symbols.get(name)
        if existing_constant:
            return existing_constant

        llvm_type = constant.type.get_llvm_type(self)
        const = ir.GlobalVariable(self._llvm_module, llvm_type, name)

        self._llvm_symbols[name] = const

        const.initializer = ir.Constant(llvm_type, constant.value)
        const.global_constant = True

        return const

    def get_or_define_llvm_symbol(self, name, definition):
        if isinstance(definition, ast.CFunctionDef):
            return self._get_or_define_llvm_function_type(
                name, definition.type
            )
        if isinstance(definition, ast.CStructDef):
            return self._get_or_define_llvm_variable_type(
                name, definition.type
            )
        if isinstance(definition, ast.CUnionDef):
            return self._get_or_define_llvm_variable_type(
                name, definition.type
            )
        # if isinstance(definition, ast.StructDef):
        #     llvm_type = definition.value.get_llvm_type(self)
        #     ir.GlobalVariable(self._llvm_module, llvm_type, name)
        if isinstance(definition, ast.ConstDef):
            # Somehow definition.value is a bytearray?
            return self._get_or_define_llvm_constant(name, definition.value)
        if isinstance(definition, ast.FunctionDef):
            return self._get_or_define_llvm_function_type(
                name, definition.type
            )

        import pdb
        pdb.set_trace()

        raise NotImplementedError()

    def get_llvm_module(self):
        if self._llvm_module:
            return self._llvm_module, self._errors

        self.parse()

        if self._errors:
            return '', self._errors

        # self._llvm_module = ir.Module(name=self.name, context=ir.Context())
        self._llvm_module = ir.Module(name=self.name)

        for name, var in self.vars.items():
            debug('compile', f'Compiling {name} {var}')
            self.get_or_define_llvm_symbol(name, var)

            if isinstance(var, ast.FunctionDef):
                self._compile_function(name, var)

            # elif isinstance(val, ast.CFunctionType):
            #     self.compile_c_function_type(val)
            # elif isinstance(val, ast.CBlockFunctionType):
            #     self.compile_c_block_function_type(val)
            # elif isinstance(val, ast.Enum):
            #     self.compile_enum(val)
            # elif isinstance(val, ast.FunctionType):
            #     self.compile_function_type(val)
            # elif isinstance(val, ast.Interface):
            #     self.compile_interface(val)
            # elif isinstance(val, ast.Range):
            #     self.compile_range(val)

        return self._llvm_module, self._errors

    def get_object_code(self):
        llvm_module, program_errors = self.get_llvm_module()
        if program_errors:
            return '', program_errors

        llvm_mod_ref = llvmlite.binding.parse_assembly(str(llvm_module))
        llvm_mod_ref.verify()

        return self.target.machine.emit_object(llvm_mod_ref), []

    def llvm_lookup(self, location, path, local_vars=None):
        fields = _IDENTIFIER_DELIMITERS.split(path)
        name = fields.pop(0)
        value = self.lookup(location, name, local_vars)

        if not value:
            raise errors.UndefinedSymbol(location, name)

        while fields:
            reflection = fields.pop(0) == '::'
            field = fields.pop(0)

            if reflection:
                value = value.reflect(location, field)
            else:
                value = value.lookup(location, field)

            if not value:
                raise errors.NoSuchField(location, field)

        return value.type.get_llvm_value(self)

    def lookup_module(self, name):
        resolved_alias = self._aliases.get(name)
        if resolved_alias:
            return resolved_alias.value

        return self._program.get_module(name)

    # pylint: disable=unused-argument
    def old_lookup(self, location, field, local_vars=None):
        debug('lookup', f'Module {self.name} looking up {field}')
        # lookup('libc')
        # lookup('Person')
        # lookup('libc.x.y.z')
        assert not '.' in field or '::' in field, (
            'Can only lookup single identifiers'
        )

        if local_vars:
            debug('lookup', 'Returning from local_vars')
            local_value = local_vars.get(field)
            if local_value is not None:
                return local_value

        resolved_alias = self._aliases.get(field)
        if resolved_alias:
            debug('lookup', f'Found alias {resolved_alias}')
            return resolved_alias.value

        local_def = self.vars.get(field)
        if local_def:
            return local_def

        module = self._program.get_module(field)
        if module:
            debug('lookup', f'Found module {module}')
            return module

        builtin = ast.BUILTIN_TYPES.get(field)
        if builtin:
            debug('lookup', f'Found builtin {module}')
            return builtin

    def _check_definition(self, definition: ast.Def):
        existing_alias = self._aliases.get(definition.name)
        if existing_alias:
            raise errors.DuplicateAlias(
                definition.location, existing_alias.location, definition.name
            )

        existing_definition = self.vars.get(definition.name)
        if existing_definition:
            raise errors.DuplicateDefinition(
                definition,
                existing_definition.location,
            )

        if definition.name in ast.BUILTIN_TYPES:
            raise errors.RedefinedBuiltIn(definition)

    # pylint: disable=no-self-use
    def reflect(self, location, name):
        return None

    def lookup(self, location, name):
        aliased_value = self._aliases.get(name)
        if aliased_value is not None:
            return aliased_value.value

        fields = _IDENTIFIER_DELIMITERS.split(name)
        first_name = fields.pop(0)

        value = self.vars.get(first_name)

        while value is not None and len(fields) > 0:
            reflection = fields.pop(0) == '::'
            field = fields.pop(0)

            if reflection:
                value = value.reflect(location, field)
            else:
                value = value.lookup(location, field)

            if not value:
                raise errors.NoSuchField(location, field)

        return value

    def lookup_type(self, location, type_name):
        aliased_value = self._aliases.get(type_name)
        if aliased_value is not None:
            return aliased_value.value

        return self.vars.get(type_name)

    def define(self, definition: ast.Def):
        self._check_definition(definition)
        if isinstance(definition, ast.AliasDef):
            debug('define', f'Alias {definition.name} -> {definition}')
            self._aliases[definition.name] = definition
        elif isinstance(definition, ast.ConstDef):
            debug('define', f'Const {definition.name} -> {definition.value}')
            self.vars[definition.name] = definition.value
        else:
            debug('define', f'Define {definition.name} -> {definition}')
            self.vars[definition.name] = definition
