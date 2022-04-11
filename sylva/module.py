import llvmlite

from llvmlite import ir

from . import ast, debug, errors, types
from .module_builder import ModuleBuilder
from .parser_utils import parse_with_listener


class Module: # pylint: disable=too-many-instance-attributes

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

    def parse(self):
        if self._parsed:
            return

        for stream in self._streams:
            module_builder = ModuleBuilder(self, stream)
            parse_with_listener(stream, module_builder)

        self._parsed = True

    def handle_expr(self, builder, expr, local_vars):
        if isinstance(expr, ast.LiteralExpr):
            return expr.get_llvm_type(self)

        if isinstance(expr, ast.SingleLookupExpr):
            value = self.llvm_lookup(expr.name, local_vars=local_vars)
            if value is None:
                raise errors.UndefinedSymbol(expr.location, expr.name)
            return value

        if isinstance(expr, ast.LookupExpr):
            ns = self.handle_expr(builder, expr.namespace, local_vars)

            if isinstance(ns, ir.Module):
                if expr.reflection:
                    raise errors.ImpossibleReflection(expr.location)
                return ns.get_global(expr.name)
            if isinstance(ns, types.CStruct):
                pass # This is a GEP call?
            if isinstance(ns, types.CUnion):
                pass # This is a bitcast and a GEP call?
            if isinstance(ns, types.Struct):
                pass # This is a GEP call?
            if isinstance(ns, types.Variant):
                pass # This is a bitcast and a GEP call?
            # [FIXME] What about `message::size`, etc.?

            # print(f"Looking up something that's not a module: {ns}")

        if isinstance(expr, ast.CallExpr):
            func = self.handle_expr(builder, expr.function, local_vars)
            args = [
                self.handle_expr(builder, arg_expr, local_vars)
                for arg_expr in expr.arguments
            ]

            for i, arg in enumerate(args):
                if isinstance(arg, ir.GlobalVariable):
                    # Have to `load` these apparently
                    args[i] = builder.load(arg)

            from pprint import pprint
            pdir = lambda x: pprint(dir(x))

            import pdb
            pdb.set_trace()

            return builder.call(func, args)

    def get_identified_type(self, name):
        return self._llvm_module.context.get_identified_type(name)

    def get_llvm_module(self):
        if self._llvm_module:
            return self._llvm_module, self._errors

        self.parse()

        for name, obj in self.vars.items():
            if isinstance(obj, types.SylvaType):
                self._errors.extend(obj.check())

            if isinstance(obj, types.MetaSylvaType):
                self._errors.extend(obj.resolve_self_references(name))

        if self._errors:
            return '', self._errors

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
                func = ir.Function(
                    self._llvm_module, obj.get_llvm_type(self), name
                )
                block = func.append_basic_block()
                builder = ir.IRBuilder(block=block)
                local_vars = dict(zip(obj.parameters.keys(), func.args))
                for node in obj.code:
                    if isinstance(node, ast.Expr):
                        self.handle_expr(builder, node, local_vars)
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
                print(f'const {var}, {var.initializer}')
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

    def lookup(self, name):
        aliased_value = self._aliases.get(name)
        if aliased_value:
            return aliased_value
        local_value = self.vars.get(name)
        if local_value:
            return local_value
        if '.' in name:
            module_name, name = name.split('.', 1)
            module = self._program.get_module(module_name)
            if module:
                return module.lookup(name)
        return types.BUILTINS.get(name)

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
