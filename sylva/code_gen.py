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
