from . import ast, errors, types

from .listener import SylvaListener
from .location import Location
from .parser import SylvaParser


def build_expr(module, location, expr):
    # print(type(expr))
    if isinstance(expr, SylvaParser.LiteralExprContext):
        literal = expr.literal()
        if literal.arrayConstLiteral():
            pass
        elif literal.functionLiteral():
            pass
        elif literal.rangeConstLiteral():
            pass
        elif literal.structConstLiteral():
            pass
        elif literal.booleanLiteral():
            return ast.BooleanLiteralExpr(location, literal.getText())
        elif literal.decimalLiteral():
            return ast.DecimalLiteralExpr(location, literal.getText())
        elif literal.floatLiteral():
            return ast.FloatLiteralExpr(location, literal.getText())
        elif literal.integerLiteral():
            return ast.IntegerLiteralExpr(location, literal.getText())
        elif literal.runeLiteral():
            return ast.RuneLiteralExpr(location, literal.getText())
        elif literal.stringLiteral():
            return ast.StringLiteralExpr(location, literal.getText())
        else:
            raise Exception(f'Unknown literal {literal} {literal.getText()}')
    elif isinstance(expr, SylvaParser.CArrayLiteralExprContext):
        pass
    elif isinstance(expr, SylvaParser.CPointerLiteralExprContext):
        pass
    elif isinstance(expr, SylvaParser.CStructLiteralExprContext):
        pass
    elif isinstance(expr, SylvaParser.CUnionLiteralExprContext):
        pass
    elif isinstance(expr, SylvaParser.CVoidLiteralExprContext):
        pass
    elif isinstance(expr, SylvaParser.IndexExprContext):
        pass
    elif isinstance(expr, SylvaParser.FunctionCallExprContext):
        return ast.CallExpr(
            location,
            build_expr(module, Location.FromContext(expr.expr()), expr.expr()),
            [
                build_expr(module, Location.FromContext(px), px)
                for px in expr.exprList().expr()
            ]
        )
    elif isinstance(expr, SylvaParser.ParamFunctionCallExprContext):
        pass
    elif isinstance(expr, SylvaParser.SingleLookupExprContext):
        return ast.SingleLookupExpr(
            location, expr.singleIdentifier().getText()
        )
    elif isinstance(expr, SylvaParser.LookupExprContext):
        lhs, rhs = expr.expr()
        return ast.LookupExpr(
            location,
            build_expr(module, Location.FromContext(lhs), lhs),
            build_expr(module, Location.FromContext(rhs), rhs),
            reflection=expr.children[1].getText() == '::'
        )
    elif isinstance(expr, SylvaParser.ParenExprContext):
        pass
    elif isinstance(expr, SylvaParser.ArrayExprContext):
        pass
    elif isinstance(expr, SylvaParser.IncDecExprContext):
        pass
    elif isinstance(expr, SylvaParser.UnaryExprContext):
        pass
    elif isinstance(expr, SylvaParser.PowerExprContext):
        pass
    elif isinstance(expr, SylvaParser.MulDivModExprContext):
        pass
    elif isinstance(expr, SylvaParser.AddSubExprContext):
        pass
    elif isinstance(expr, SylvaParser.ShiftExprContext):
        pass
    elif isinstance(expr, SylvaParser.CmpExprContext):
        pass
    elif isinstance(expr, SylvaParser.BandExprContext):
        pass
    elif isinstance(expr, SylvaParser.BxorExprContext):
        pass
    elif isinstance(expr, SylvaParser.BorExprContext):
        pass
    elif isinstance(expr, SylvaParser.AndExprContext):
        pass
    elif isinstance(expr, SylvaParser.OrExprContext):
        pass
    elif isinstance(expr, SylvaParser.OwnedPointerExprContext):
        pass
    elif isinstance(expr, SylvaParser.ReferenceExprContext):
        pass
    else:
        raise Exception(f'Unknown expr type {type(expr)} ({expr.getText()})')


def build_code_block(module, location, code_block):
    code = []
    for c in code_block.children[1:-1]:
        if code_block.ifBlock():
            pass
        elif code_block.switchBlock():
            pass
        elif code_block.matchBlock():
            pass
        elif code_block.forBlock():
            pass
        elif code_block.whileBlock():
            pass
        elif code_block.loopBlock():
            pass
        elif code_block.letStmt():
            pass
        elif code_block.assignStmt():
            pass
        elif code_block.returnStmt():
            pass
        elif code_block.breakStmt():
            pass
        elif code_block.continueStmt():
            pass
        elif code_block.expr():
            for x in code_block.expr():
                code.append(build_expr(module, Location.FromContext(x), x))
        else:
            raise Exception(f'Unknown code block child {c.getText()}')
    return code


def build_function_from_type_literal(module, location, literal):
    # yapf: disable
    return types.Function(
        location,
        build_param_list_from_type_literal_pairs(
            module,
            literal.typeLiteralPairList()
        ),
        get_or_create_type_literal(
            module,
            Location.FromContext(literal.typeLiteral()),
            literal.typeLiteral()
        ) if (hasattr(literal, 'typeLiteral')
              and literal.typeLiteral()) else None,
        build_code_block(
            module,
            Location.FromContext(literal.codeBlock()),
            literal.codeBlock()
        )
    )

def build_param_list_from_type_literal_pairs(module, pairs):
    # yapf: disable
    return {
        param_name.getText(): get_or_create_type_literal(
            module,
            Location.FromContext(type_literal),
            type_literal
        )
        for param_name, type_literal in zip(
            pairs.singleIdentifier(),
            pairs.typeLiteral()
        )
    }


def build_cstruct_from_type_literal(module, location, literal):
    return types.CStruct(
        location,
        build_param_list_from_type_literal_pairs(
            module,
            literal.typeLiteralPairList()
        ),
    )


def build_cunion_from_type_literal(module, location, literal):
    return types.CUnion(
        location,
        build_param_list_from_type_literal_pairs(
            module,
            literal.typeLiteralPairList()
        ),
    )


def build_cfunction_from_type_literal(module, location, literal):
    return types.CFunction(
        location,
        build_param_list_from_type_literal_pairs(
            module,
            literal.typeLiteralPairList()
        ),
        get_or_create_type_literal(
            module,
            Location.FromContext(literal.typeLiteral()),
            literal.typeLiteral()
        ) if hasattr(literal, 'typeLiteral') and literal.typeLiteral() else None
    )


def get_or_create_type_literal(module, location, literal):
    if isinstance(literal, types.SylvaType):
        return literal
    if literal.arrayTypeLiteral():
        pass
    if literal.carrayTypeLiteral():
        carray = literal.carrayTypeLiteral()
        return types.CArray(
            location,
            get_or_create_type_literal(
                module,
                Location.FromContext(carray.typeLiteral()),
                carray.typeLiteral()
            ),
            int(carray.intDecimalLiteral().getText()) if (
                hasattr(carray, 'intDecimalLiteral') and
                carray.intDecimalLiteral()
            ) else None
        )
    if literal.cbitfieldTypeLiteral():
        cbitfield = literal.cbitfieldTypeLiteral()
        return types.CBitField(
            location,
            cbitfield.INT_TYPE().getText(),
            cbitfield.INT_TYPE().getText().startswith('i'),
            int(cbitfield.intDecimalLiteral().getText())
        )
    if literal.cblockfunctionTypeLiteral():
        cblockfntype = literal.cblockfunctionTypeLiteral().functionTypeLiteral()
        return types.CFunctionType(
            location,
            build_param_list_from_type_literal_pairs(
                module,
                cblockfntype.typeLiteralPairList()
            ),
            get_or_create_type_literal(
                module,
                Location.FromContext(cblockfntype.typeLiteral()),
                cblockfntype.typeLiteral()
            ) if (hasattr(cblockfntype, 'typeLiteral')
                  and cblockfntype.typeLiteral()) else None
        )
    if literal.cfunctionTypeLiteral():
        cfntype = literal.cfunctionTypeLiteral().functionTypeLiteral()
        return types.CFunctionType(
            location,
            build_param_list_from_type_literal_pairs(
                module,
                cfntype.typeLiteralPairList()
            ),
            get_or_create_type_literal(
                module,
                Location.FromContext(cfntype.typeLiteral()),
                cfntype.typeLiteral()
            ) if (hasattr(cfntype, 'typeLiteral')
                  and cfntype.typeLiteral()) else None
        )
    if literal.cpointerTypeLiteral():
        text = literal.getText()
        referenced_type = None
        referenced_type_is_mutable = False
        is_mutable = False

        if text.endswith('!'):
            is_mutable = True
            text = text[:-1]

        text = text[5:-1]

        if text.endswith('!'):
            referenced_type_is_mutable = True
            text = text[:-1]

        referenced_type = text

        return types.CPtr(
            location, referenced_type, referenced_type_is_mutable, is_mutable
        )
    if literal.cstructTypeLiteral():
        pass
    if literal.cunionTypeLiteral():
        pass
    if literal.cvoidTypeLiteral():
        return module.lookup('cvoid')
    if literal.functionTypeLiteral():
        pass
    if literal.identifier():
        name = literal.getText()
        value = module.lookup(name)
        if value is None:
            raise errors.UndefinedSymbol(location, name)
        return get_or_create_type_literal(module, location, value)
    if literal.paramTypeLiteral():
        pass
    if literal.rangeTypeLiteral():
        pass
    if literal.structTypeLiteral():
        pass

    raise Exception(f'Unknown type literal {literal.getText()}')


def eval_const_literal(location, literal):
    if literal.arrayConstLiteral():
        pass
    elif literal.booleanLiteral():
        pass
    elif literal.decimalLiteral():
        pass
    elif literal.floatLiteral():
        pass
    elif literal.functionLiteral():
        pass
    elif literal.integerLiteral():
        return ast.IntegerLiteralExpr(location, literal.getText())
    elif literal.rangeConstLiteral():
        pass
    elif literal.runeLiteral():
        pass
    elif literal.stringLiteral():
        return ast.StringLiteralExpr(location, literal.getText())
    elif literal.structConstLiteral():
        pass


def lookup_identifier(module, identifier):
    location = Location.FromContext(identifier)
    name = identifier.getText()
    value = module.lookup(name)
    if value is None:
        raise errors.UndefinedSymbol(location, name)
    return value


class ModuleBuilder(SylvaListener):

    def __init__(self, module):
        self.module = module

    def exitAliasDef(self, ctx):
        if ctx.identifier():
            target = lookup_identifier(self.module, ctx.identifier())
        elif ctx.typeLiteral():
            target = get_or_create_type_literal(
                self.module,
                Location.FromContext(ctx.typeLiteral()),
                ctx.typeLiteral()
            )
        else:
            raise Exception(f'Malformed alias def: {ctx.getText()}')
        self.module.add_alias(ctx.singleIdentifier().getText(), target)

    def exitConstDef(self, ctx):
        const_expr = ctx.constExpr()
        if const_expr.identifier():
            target = eval_const_literal(
                Location.FromContext(const_expr.identifier()),
                lookup_identifier(self.module, const_expr.identifier())
            )
        elif const_expr.literal():
            target = eval_const_literal(
                Location.FromContext(const_expr.literal()),
                const_expr.literal()
            )
        else:
            raise Exception(f'Malformed const def: {ctx.getText()}')
        self.module.define(ctx.singleIdentifier().getText(), target)

    def exitCfunctionTypeDef(self, ctx):
        self.module.define(
            ctx.singleIdentifier().getText(),
            build_cfunction_from_type_literal(
                self.module,
                Location.FromContext(ctx.functionTypeLiteral()),
                ctx.functionTypeLiteral()
            )
        )

    def exitCunionTypeDef(self, ctx):
        self.module.define(
            ctx.singleIdentifier().getText(),
            build_cunion_from_type_literal(
                self.module,
                Location.FromContext(ctx),
                ctx
            )
        )

    def exitCstructTypeDef(self, ctx):
        self.module.define(
            ctx.singleIdentifier().getText(),
            build_cstruct_from_type_literal(
                self.module,
                Location.FromContext(ctx),
                ctx
            )
        )

    def exitFunctionDef(self, ctx):
        self.module.define(
            ctx.singleIdentifier().getText(),
            build_function_from_type_literal(
                self.module,
                Location.FromContext(ctx.functionLiteral()),
                ctx.functionLiteral()
            )
        )
