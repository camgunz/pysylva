import llvmlite # type: ignore

from llvmlite import ir

# pylint: disable=unused-import
from . import ast, debug, errors


class CodeGen:

    def __init__(self, module):
        self._module = module
        self._errors = []
        self._llvm_module = None

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
        while isinstance(expr, ast.BaseLookupExpr):
            if isinstance(expr, ast.LookupExpr):
                local_var = local_vars.get(expr.name)
                if local_var is not None:
                    expr = local_var

                var = self.vars.get(expr.name)
                if var is not None:
                    expr = var

                raise errors.UndefinedSymbol(expr.location, expr.name)
            elif isinstance(expr, ast.AttributeLookupExpr):
                ns_expr = self._resolve_lookup_expr(expr.expr, local_vars)
                if expr.reflection:
                    if not isinstance(ns_expr.type, ast.Reflectable):
                        raise errors.ImpossibleReflection(expr.location)
                    field = ns_expr.reflect
                else:
                    if not isinstance(ns_expr.type, ast.Dotable):
                        raise errors.ImpossibleLookup(expr.location)

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

    def _reduce_expr(self, expr, local_vars):
        debug('compile_expr', f'_reduce_expr: {expr}')

        if isinstance(expr, ast.LookupExpr):
            pass

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
            obj = self._reduce_expr(expr.expr, local_vars)

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

        if isinstance(expr, ast.Parameter):
            # [FIXME] These have to be expressions, WTF is a parameter
            #         gonna do here.
            # Get the type
            pass

        if isinstance(expr, ast.CallExpr):
            pass

        if isinstance(expr, ast.StructDef):
            pass

        if isinstance(expr, ast.CStructDef):
            pass

        if isinstance(expr, ast.VariantDef):
            pass

        if isinstance(expr, ast.CUnionDef):
            pass

        # if isinstance(expr, ast.InterfaceDef):
        #     pass

        # if isinstance(expr, ast.EnumDef):
        #     pass

        if is_reflection:
            pass

        res = local_vars.get(expr.name)

        if res is not None:
            value = res[1] # LLVM value
        else:
            value = expr.object.lookup(expr.location, expr.name)
            if value is not None:
                value = self.get_or_define_llvm_symbol(expr.name, value)

        if value is None:
            raise errors.NoSuchAttribute(expr.location, expr.name)

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
            func = self._reduce_expr(expr.function, params, local_vars)
            args = [
                self._reduce_expr(arg_expr, params, local_vars)
                for arg_expr in expr.arguments
            ]

            return builder.call(func, [builder.load(arg) for arg in args])

        if isinstance(expr, ast.CPointerCastExpr):
            value = self._reduce_expr(expr.value, params, local_vars)
            if value.type.is_pointer:
                return value

            stack_slot = builder.alloca(value.type)
            builder.store(value, stack_slot)
            return stack_slot

        if isinstance(expr, ast.CVoidCastExpr):
            value = self._reduce_expr(expr.value, params, local_vars)
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
            value = self._reduce_expr(expr.object, params, local_vars)
            if not isinstance(value, ast.ValueExpr):
                import pdb
                pdb.set_trace()
                raise Exception('Non-value-expr stored as a value expr')
            return self._reduce_expr(
                value.reflect(expr.location, expr.name), params, local_vars
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
    def _compile_function(self, function_type, code):
        # "function_type" is a little confusing here. It's a Sylva
        # MonoFunctionType.
        block = function_type.llvm_value.append_basic_block()
        builder = ir.IRBuilder(block=block)
        params = function_type.parameters
        code_block_vars = {}
        for arg, param in zip(function_type.llvm_value.args, params):
            param_llvm_type = param.type.get_llvm_type(self._module)
            alloca = builder.alloca(param_llvm_type, name=param.name)
            value_expr = param.type.get_value_expr(param.location, alloca)
            builder.store(arg, value_expr.llvm_value)
            code_block_vars[param.name] = value_expr
        self._compile_code_block(code, builder, code_block_vars)

    def _compile_code_block(self, code, builder, local_vars):
        for node in code:
            if isinstance(node, ast.Expr):
                expr = self._reduce_expr(node, local_vars)

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
            if name in ast.BUILTIN_TYPES:
                continue

            if isinstance(var, ast.Const):
                debug('compile', f'Compiling constant {name}')
                llvm_type = var.type.get_llvm_type(self._module)
                const = ir.GlobalVariable(self._llvm_module, llvm_type, name)
                const.initializer = ir.Constant(llvm_type, var.value.value)
                const.global_constant = True
                var.llvm_value = const
            elif isinstance(var, ast.CFunction):
                debug('compile', f'Compiling cfn {name}')
                var.llvm_value = ir.Function(
                    self._llvm_module,
                    var.type.get_llvm_type(self._module),
                    name
                )
            elif isinstance(var, ast.CStruct):
                var.llvm_value = ir.GlobalVariable(
                    self._llvm_module, var.get_llvm_type(self._module), name
                )
            elif isinstance(var, ast.CUnion):
                var.llvm_value = ir.GlobalVariable(
                    self._llvm_module, var.get_llvm_type(self._module), name
                )
            # elif isinstance(var, ast.Struct):
            #     llvm_type = var.value.get_llvm_type(self._module)
            #     ir.GlobalVariable(self._llvm_module, llvm_type, name)
            elif isinstance(var, ast.Function):
                for mm in var.type.monomorphizations:
                    llvm_type = mm.get_llvm_type(self._module)
                    if var.type.is_polymorphic:
                        func_name = f'_Sylva_{mm.type.mangle()}'
                    else:
                        func_name = name
                    mm.llvm_value = ir.Function(
                        self._llvm_module, llvm_type, func_name
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

        return self._module.target.machine.emit_object(llvm_mod_ref), []

    def get_identified_type(self, name):
        return self._llvm_module.context.get_identified_type(name)
