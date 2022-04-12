import llvmlite

from llvmlite import ir

# pylint: disable=unused-import
from . import ast, debug, errors, types
from .location import Location
from .module_builder import ModuleBuilder
from .parser_utils import parse_with_listener


class Module:

    def __init__(self, program, name, streams, requirement_statements):
        self._program = program
        self._name = name
        self._streams = streams
        self._requirement_statements = requirement_statements
        self._parsed = False
        self._errors = []
        self._llvm_module = None

        self._aliases = {}
        self.vars = {}
        self.requirements = set()
        self.type = types.Module(Location.Generate(), self)

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
            if isinstance(obj, types.SylvaType):
                self._errors.extend(obj.check())

            if isinstance(obj, types.MetaSylvaType):
                self._errors.extend(obj.resolve_self_references(name))

        self._parsed = True

        return self._errors

    def _handle_expr(self, builder, expr, local_vars):
        if isinstance(expr, ast.Literal):
            return expr.get_llvm_type(self)

        if isinstance(expr, ast.SingleLookupExpr):
            value = None

            value = local_vars.get(expr.name)

            if value is None:
                value = self.lookup(
                    expr.name, expr.location, local_vars=local_vars
                )

            if value is None:
                raise errors.UndefinedSymbol(expr.location, expr.name)

            if isinstance(value, ir.GlobalVariable):
                value = builder.load(value)

            return value

        if isinstance(expr, ast.LookupExpr):
            # What might this be:
            # - a local variable (argument, assignment)
            #   - struct, enum, interface, variant, array (?)
            # - a module
            ns = self._handle_expr(builder, expr.namespace, local_vars)

            if isinstance(ns, ir.Module) and expr.reflection:
                raise errors.ImpossibleReflection(expr.location)

            # At this point, ns could be something like LLVM-friendly like a
            # Struct, or LLVM-unfriendly like an Interface. Regardless, we're
            # doing `.lookup` on all of it.

            value = ns.lookup(expr.name, expr.location)

            if isinstance(value, ir.GlobalVariable):
                value = builder.load(value)

            return value

        if isinstance(expr, ast.Call):
            func = self._handle_expr(builder, expr.function, local_vars)
            args = [
                self._handle_expr(builder, arg_expr, local_vars)
                for arg_expr in expr.arguments
            ]

            return builder.call(func, args)

        if isinstance(expr, ast.CPointer):
            return expr

    def _handle_function(self, name, func):
        llvm_func = ir.Function(
            self._llvm_module, func.get_llvm_type(self), name
        )
        block = llvm_func.append_basic_block()
        builder = ir.IRBuilder(block=block)
        local_vars = dict(zip(func.parameters.keys(), llvm_func.args))
        for node in func.code:
            if isinstance(node, ast.Expr):
                self._handle_expr(builder, node, local_vars)

    def get_llvm_module(self):
        if self._llvm_module:
            return self._llvm_module, self._errors

        self.parse()

        if self._errors:
            return '', self._errors

        print('Building LLVM module')
        # self._llvm_module = ir.Module(name=self.name, context=ir.Context())
        self._llvm_module = ir.Module(name=self.name)

        for name, obj in self.vars.items():
            if isinstance(obj, types.CFunction):
                ir.Function(self._llvm_module, obj.get_llvm_type(self), name)
            elif isinstance(obj, types.CStruct):
                ir.GlobalVariable(
                    self._llvm_module, obj.get_llvm_type(self, name), name
                )
            elif isinstance(obj, types.CUnion):
                ir.GlobalVariable(
                    self._llvm_module, obj.get_llvm_type(self), name
                )
            elif isinstance(obj, types.Function):
                self._handle_function(name, obj)
            elif isinstance(obj, types.Struct):
                ir.GlobalVariable(
                    self._llvm_module, obj.get_llvm_type(self), name
                )
            elif isinstance(obj, types.ConstDef):
                var = ir.GlobalVariable(
                    self._llvm_module, obj.value.get_llvm_type(self), name
                )
                var.initializer = obj.value.get_llvm_value(self)
                var.global_constant = True
            # elif isinstance(obj, types.CFunctionType):
            #     self.compile_c_function_type(obj)
            # elif isinstance(obj, types.CBlockFunctionType):
            #     self.compile_c_block_function_type(obj)
            # elif isinstance(obj, types.Enum):
            #     self.compile_enum(obj)
            # elif isinstance(obj, types.FunctionType):
            #     self.compile_function_type(obj)
            # elif isinstance(obj, types.Interface):
            #     self.compile_interface(obj)
            # elif isinstance(obj, types.Range):
            #     self.compile_range(obj)

        return self._llvm_module, self._errors

    def get_object_code(self):
        llvm_module, program_errors = self.get_llvm_module()
        if program_errors:
            return '', program_errors

        llvm_mod_ref = llvmlite.binding.parse_assembly(str(llvm_module))
        llvm_mod_ref.verify()

        return self.target.machine.emit_object(llvm_mod_ref), []

    def add_alias(self, name, value):
        existing_alias = self._aliases.get(name)
        if existing_alias:
            raise errors.DuplicateAlias(
                value.location, existing_alias.location, name
            )
        self._aliases[name] = value

    def llvm_lookup(self, name, local_vars=None):
        if local_vars:
            value = local_vars.get(name)
            if value:
                return value

        aliased_name = self._aliases.get(name)
        if aliased_name:
            name = aliased_name

        module = self._program.get_module(name)
        if module:
            return module.llvm_module

        try:
            return self._llvm_module.get_global(name)
        except KeyError:
            pass

    # pylint: disable=unused-argument
    def lookup(self, location, field, local_vars=None):
        # lookup('libc')
        # lookup('Person')
        # lookup('libc.x.y.z')
        assert not '.' in field or '::' in field, (
            'Can only lookup single identifiers'
        )

        if local_vars:
            local_value = local_vars.get(field)
            if local_value is not None:
                return local_value

        aliased_value = self._aliases.get(field)
        if aliased_value:
            return aliased_value

        local_value = self.vars.get(field)
        if local_value:
            return local_value

        module = self._program.get_module(field)
        if module:
            return module

        builtin = types.BUILTINS.get(field)
        if builtin:
            return builtin

    # pylint: disable=no-self-use
    def reflect(self, location, field):
        raise errors.ImpossibleReflection(location)

    def define(self, name, value):
        existing_value = self.vars.get(name)
        if existing_value:
            raise errors.DuplicateDefinition(
                value.location, existing_value.location
            )

        if '.' in name and self._program.get_module(name.split('.', 1)[0]):
            raise errors.DefinitionViolation(value.location, name)

        if name in types.BUILTINS:
            raise errors.RedefinedBuiltIn(value.location, name)

        self.vars[name] = value
