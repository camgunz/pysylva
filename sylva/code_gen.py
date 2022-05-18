import llvmlite # type: ignore

from llvmlite import ir

# pylint: disable=unused-import
from . import ast, debug, errors
from .target import get_target


class CodeGen:

    def __init__(self, module):
        self._module = module
        self._errors = []
        self._llvm_module = None

    """
    def _resolve_lookup_expr(self, expr, local_vars):
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
        attr = expr
        while isinstance(attr, ast.BaseLookupExpr):
            elif isinstance(attr, ast.AttributeLookupExpr):
                ns_expr = self._resolve_lookup_expr(attr.expr, local_vars)
                if attr.reflection:
                    if not isinstance(ns_expr.type, ast.Reflectable):
                        raise errors.ImpossibleReflection(attr.location)
                    attr = ns_expr.reflect_attribute(attr.location, attr.name)
                elif not isinstance(ns_expr.type, ast.Dotable):
                    raise errors.ImpossibleLookup(attr.location)
                else:
                    attr = ns_expr.emit_attribute_lookup(attr.location, attr.name)

                # What will have happened is:
                # AttributeLookupExpr(LookupExpr('libc'), 'write', ref=False)
                # AttributeLookupExpr(LookupExpr('message'), 'size', ref=True)

                # At this point we have an expr:
                # - LiteralExpr
                # - ValueExpr
                # - Module (?)
                #
                # We're still dealing with Sylva objects, so we can just start
                # calling `lookup` methods

                if not isinstance(ns_expr.type, ast.Lookupable):
                    pass

        return expr
        """

    def _compile_expr(self, expr, builder, local_vars):
        debug('compile_expr', f'_compile_expr: {expr}')
        from .module import Module

        if isinstance(expr, Module):
            return expr

        if isinstance(expr, ast.LookupExpr):
            var = local_vars.get(expr.name)

            if var is None:
                var = self._module.emit_attribute_lookup(
                    expr.location, expr.name
                )

            if var is None:
                raise errors.UndefinedSymbol(expr.location, expr.name)

            return self._compile_expr(var, builder, local_vars)

        if isinstance(expr, ast.AttributeLookupExpr):
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
            nex = self._compile_expr(expr.expr, builder, local_vars)
            while isinstance(nex, ast.AttributeLookupExpr):
                if nex.reflection:
                    if not isinstance(nex.type, ast.Reflectable):
                        raise errors.ImpossibleReflection(nex.location)
                    nex = nex.reflect_attribute(nex.location, nex.attribute)
                elif not isinstance(nex.type, ast.Dotable):
                    raise errors.ImpossibleLookup(nex.location)
                else: # [FIXME] This will only work for depth-1 lookups
                    nex = nex.emit_attribute_lookup(
                        nex.location, nex.attribute
                    )

            return self._compile_expr(nex, builder, local_vars)
            # The tactic here is to rollup the things we can into a single
            # GEP ((c)structs and (c)arrays), other

            # This is all different depending on what obj is. If it's an
            # enum we're looking at some kind of constant. If it's a struct
            # we're doing a GEP. Etc. etc.

            # We're basically walking through the lookups here, trying to
            # decide what kind of code to generate. Type lookups are the
            # name of the game here, e.g. if it's like blah.call().bloo,
            # we have to figure out what blah is, what blah.call is, what
            # what blah.call returns, and then what bloo is inside of that.
            #
            # I think we can leverage Dotable and Reflectable here? We know
            # the types of everything, so we can at least check for impossible
            # lookups and reflections.

        if isinstance(expr, ast.ValueExpr):
            # [FIXME] These have to be expressions, WTF is a parameter
            #         gonna do here.
            # Get the type
            return expr.emit(self._module, builder)

        if isinstance(expr, ast.CallExpr):
            return expr.emit(self._module, builder)

        if isinstance(expr, ast.Struct):
            pass

        if isinstance(expr, ast.CStruct):
            pass

        if isinstance(expr, ast.CUnion):
            pass

        if isinstance(expr, ast.InterfaceType):
            return # [TODO]

        if isinstance(expr, ast.EnumType):
            return # [TODO]

        if isinstance(expr, ast.Variant):
            pass

        if isinstance(expr, ast.CPointerExpr):
            value = self._compile_expr(expr.value, builder, local_vars)
            if value.type.is_pointer:
                return value

            stack_slot = builder.alloca(value.type)
            builder.store(value, stack_slot)
            return stack_slot

        if isinstance(expr, ast.CVoidExpr):
            value = self._compile_expr(expr.value, builder, local_vars)
            return builder.bitcast(value, ir.IntType(8).as_pointer())

        import pdb
        pdb.set_trace()

        raise NotImplementedError()

    # pylint: disable=too-many-locals
    def _compile_function(self, function_type, code):
        # "function_type" is a little confusing here. It's a Sylva
        # MonoFunctionType.
        block = function_type.llvm_value.append_basic_block()
        builder = ir.IRBuilder(block=block)
        params = function_type.parameters
        code_block_vars = {}
        for arg, param in zip(function_type.llvm_value.args, params):
            alloca = builder.alloca(param.type.llvm_type, name=param.name)
            value_expr = param.type.get_value_expr(param.location)
            value_expr.llvm_value = alloca
            builder.store(arg, value_expr.llvm_value)
            code_block_vars[param.name] = value_expr
        self._compile_code_block(code, builder, code_block_vars)

    def _compile_code_block(self, code, builder, local_vars):
        for node in code:
            if isinstance(node, ast.Expr):
                expr = self._compile_expr(node, builder, local_vars)

    def get_llvm_module(self):
        from .module import Module

        if self._llvm_module is not None:
            return self._llvm_module, self._errors

        # self._llvm_module = ir.Module(
        #   name=self._modulename, context=ir.Context()
        # )
        self._llvm_module = ir.Module(name=self._module.name)

        # This is where we type check things

        # First step here is to monomorphize functions that take strings.
        # We have to find all functions that take strings, then find any call
        # sites for those functions

        for name, var in self._module.vars.items():
            # if name in ast.BUILTIN_TYPES:
            #     continue

            if isinstance(var, ast.Const):
                debug('compile', f'Compiling constant {name}')
                llvm_type = var.type.llvm_type
                const = ir.GlobalVariable(self._llvm_module, llvm_type, name)
                const.initializer = ir.Constant(llvm_type, var.value.value)
                const.global_constant = True
                var.llvm_value = const
            elif isinstance(var, ast.CFunction):
                debug('compile', f'Compiling cfn {name}')
                var.llvm_value = ir.Function(
                    self._llvm_module, var.type.llvm_type, name
                )
            elif isinstance(var, ast.CStruct):
                var.llvm_value = ir.GlobalVariable(
                    self._llvm_module, var.llvm_type, name
                )
            elif isinstance(var, ast.CUnion):
                var.llvm_value = ir.GlobalVariable(
                    self._llvm_module, var.llvm_type, name
                )
            # elif isinstance(var, ast.Struct):
            #     llvm_type = var.value.llvm_type
            #     ir.GlobalVariable(self._llvm_module, llvm_type, name)
            elif isinstance(var, ast.Function):
                for mm in var.type.monomorphizations:
                    if var.type.is_polymorphic:
                        func_name = f'_Sylva_{mm.type.mangle()}'
                    else:
                        func_name = name
                    mm.llvm_value = ir.Function(
                        self._llvm_module, mm.llvm_type, func_name
                    )
                    self._compile_function(mm, var.code)
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
            elif isinstance(var, Module):
                pass
            else:
                import pdb
                pdb.set_trace()
                raise NotImplementedError()

        return self._llvm_module, self._errors

    def get_object_code(self):
        llvm_module, program_errors = self.get_llvm_module()
        if program_errors:
            return b'', program_errors

        llvm_mod_ref = llvmlite.binding.parse_assembly(str(llvm_module))
        llvm_mod_ref.verify()

        return get_target().machine.emit_object(llvm_mod_ref), []

    def get_identified_type(self, name):
        return self._llvm_module.context.get_identified_type(name)
