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
        if not self._parsed:
            for stream in self._streams:
                module_builder = ModuleBuilder(self, stream)
                parse_with_listener(stream, module_builder)
            self._parsed = True

    def eval_const_expr(self, expr):
        pass

    def get_identified_type(self, name):
        self._llvm_module.context.get_identified_type(name)

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
                debug('compile', f'Adding cfunction {name}')
                ir.Function(self._llvm_module, obj.get_llvm_type(self), name)
            elif isinstance(obj, types.CStruct):
                debug('compile', f'Adding cstruct {name}')
                ir.GlobalVariable(
                    self._llvm_module, obj.get_llvm_type(self, name), name
                )
            elif isinstance(obj, types.CUnion):
                debug('compile', f'Adding cunion {name}')
                ir.GlobalVariable(
                    self._llvm_module, obj.get_llvm_type(self), name
                )
            elif isinstance(obj, types.Function):
                debug('compile', f'Adding function {name}')
                func = ir.Function(
                    self._llvm_module, obj.get_llvm_type(self), name
                )
                block = func.append_basic_block()
                builder = ir.IRBuilder(block=block)
                for node in obj.code:
                    if isinstance(node, ast.CallExpr):
                        builder.call(
                            self.eval_const_expr(node.function),
                            [
                                self.eval_const_expr(arg)
                                for arg in node.arguments
                            ]
                        )
                        # This is weird because we kind of rebuild all the LLVM
                        # types ourselves. We need to lookup the function in
                        # the module, but not the Sylva function and Sylva
                        # Module, the LLVM function and LLVM module. How to do
                        # that?

                        # llvm_func = self.llvm_lookup(
                        #   module._program, self._llvm_module, node.function
                        # )
                        # self.handle_function_call(node, builder)

                # [TODO] Handle code block
            elif isinstance(obj, types.Struct):
                debug('compile', f'Adding struct {name}')
                ir.GlobalVariable(
                    self._llvm_module, obj.get_llvm_type(self), name
                )
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
        debug('module_builder', f'alias {name} -> {value}')
        existing_alias = self._aliases.get(name)
        if existing_alias:
            raise errors.DuplicateAlias(
                value.location, existing_alias.location, name
            )
        self._aliases[name] = value

    def llvm_lookup(self, name):
        local_value = self._llvm_module.get_global(name)
        if local_value:
            return local_value
        if '.' in name:
            module_name, name = name.split('.', 1)
            module = self._program.get_module(module_name)
            if module:
                return module.llvm_lookup(name)

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
        debug('module_builder', f'define {self.name}.{name} -> {value}')
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

    # def define_cstruct(self, name, cstruct):
    #     self.vars
