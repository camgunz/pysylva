import re

import llvmlite # type: ignore

from llvmlite import ir

# pylint: disable=unused-import
from . import ast, debug, errors
from .location import Location
from .module_builder import ModuleBuilder
from .parser_utils import parse_with_listener


_IDENTIFIER_DELIMITERS = re.compile(r'(\.|::)')


class Module:

    def __init__(self, program, name, streams, requirement_statements):
        self._program = program
        self._name = name
        self._streams = streams
        self._requirement_statements = requirement_statements
        self._parsed = False
        self._errors = []
        self._llvm_module = None
        self._definitions = {}

        self.vars = {}
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
        for requirement in self.requirements:
            requirement.resolve_requirements(seen)

    def get_identified_type(self, name):
        return self._llvm_module.context.get_identified_type(name)

    def parse(self):
        if self._parsed:
            return self._errors

        for stream in self._streams:
            module_builder = ModuleBuilder(self, stream)
            parse_with_listener(stream, module_builder)

        for name, obj in self.vars.items():
            if isinstance(obj, ast.SylvaType):
                self._errors.extend(obj.check())

            if isinstance(obj, ast.MetaSylvaType):
                self._errors.extend(obj.resolve_self_references(name))

        self._parsed = True

        return self._errors

    def _compile_expr(self, builder, expr, local_vars):
        debug('compile_expr', f'_compile_expr: {expr}')
        if isinstance(expr, ast.LiteralExpr):
            return expr.get_llvm_value(self)

        # if isinstance(expr, ast.ConstExpr):
        #     # This catches CVoidCast and MoveExpr... why?
        #     pass

        if isinstance(expr, ast.ValueExpr):
            return self.llvm_lookup(expr.location, expr.name, local_vars)

        if isinstance(expr, ast.FieldLookupExpr):
            # return builder.gep(?)
            pass

        if isinstance(expr, ast.CallExpr):
            func = self._compile_expr(builder, expr.function, local_vars)
            args = [
                self._compile_expr(builder, arg_expr, local_vars)
                for arg_expr in expr.arguments
            ]

            return builder.call(func, args)

        if isinstance(expr, ast.CPointerExpr):
            return expr

    # pylint: disable=too-many-locals
    def _compile_function(self, name, function_def):
        function = function_def.value
        llvm_type = function.type.get_llvm_type(self)
        llvm_func = ir.Function(self._llvm_module, llvm_type, name)
        block = llvm_func.append_basic_block()
        builder = ir.IRBuilder(block=block)
        params = function.parameters.items()
        local_vars = {}
        for arg, param_name_and_param_type in zip(llvm_func.args, params):
            param_name, param_type = param_name_and_param_type
            param_llvm_type = param_type.get_llvm_type(self)
            stack_slot = builder.alloca(param_llvm_type, name=param_name)
            builder.store(arg, stack_slot)
            local_vars[arg.name] = stack_slot
        self._compile_code_block(function.code, builder, local_vars)

    def _compile_code_block(self, code, builder, local_vars):
        for node in code:
            if isinstance(node, ast.Expr):
                self._compile_expr(builder, node, local_vars)

    def get_llvm_module(self):
        if self._llvm_module:
            return self._llvm_module, self._errors

        self.parse()

        if self._errors:
            return '', self._errors

        print('Building LLVM module')
        # self._llvm_module = ir.Module(name=self.name, context=ir.Context())
        self._llvm_module = ir.Module(name=self.name)

        for name, var in self.vars.items():
            debug('compile', f'Compiling {name} {var}')
            if isinstance(var, ast.CFunctionDef):
                llvm_type = var.value.get_llvm_type(self)
                ir.Function(self._llvm_module, llvm_type, name)
            elif isinstance(var, ast.CStructDef):
                llvm_type = var.value.get_llvm_type(self, name)
                ir.GlobalVariable(self._llvm_module, llvm_type, name)
            elif isinstance(var, ast.CUnionDef):
                llvm_type = var.value.get_llvm_type(self)
                ir.GlobalVariable(self._llvm_module, llvm_type, name)
            elif isinstance(var, ast.FunctionDef):
                self._compile_function(name, var)
            # elif isinstance(var, ast.StructDef):
            #     llvm_type = var.value.get_llvm_type(self)
            #     ir.GlobalVariable(self._llvm_module, llvm_type, name)
            elif isinstance(var, ast.ConstDef):
                val = var.value # These are literals
                llvm_type = val.value.get_llvm_type(self)
                var = ir.GlobalVariable(self._llvm_module, llvm_type, name)
                var.initializer = val.value.get_llvm_value(self)
                var.global_constant = True
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

        print(str(llvm_module))

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

    # pylint: disable=unused-argument
    def lookup(self, location, field, local_vars=None):
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

        local_def = self.vars.get(field)
        if local_def:
            return local_def

        module = self._program.get_module(field)
        if module:
            debug('lookup', 'Returning a module')
            return module

        builtin = ast.BUILTIN_TYPES.get(field)
        if builtin:
            debug('lookup', 'Returning a builtin')
            return builtin

    # pylint: disable=no-self-use
    def reflect(self, location, field):
        raise errors.ImpossibleReflection(location)

    def add_definition(self, definition: ast.Def):
        existing_def = self._definitions.get(definition.name)
        if existing_def:
            raise errors.DuplicateDefinition(
                definition.location, existing_def.location
            )

        if definition.name in ast.BUILTIN_TYPES:
            raise errors.RedefinedBuiltIn(definition.location, definition.name)

        self.vars[definition.name] = definition.value
        self._definitions[definition.name] = definition.location
