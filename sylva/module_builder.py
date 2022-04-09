import enum

from . import ast, debug, errors, types

from .listener import SylvaParserListener
from .location import Location
from .parser import SylvaParser


class TypeModifier(enum.Enum):
    Raw = enum.auto()
    Pointer = enum.auto()
    Reference = enum.auto()
    ExclusiveReference = enum.auto()

    @classmethod
    def FromTypeLiteral(cls, type_literal):
        first_child = type_literal.children[0].getText()
        last_child = type_literal.children[-1].getText()

        if first_child == '*':
            return cls.Pointer

        if not first_child == '&':
            return cls.Raw

        if last_child == '!':
            return cls.ExclusiveReference

        return cls.Reference


class ModuleBuilder(SylvaParserListener):

    def __init__(self, module, stream):
        self.module = module
        self.stream = stream

    def build_expr(self, location, expr):
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
                raise Exception(
                    f'Unknown literal {literal} {literal.getText()}'
                )
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
                self.build_expr(
                    Location.FromContext(expr.expr(), self.stream),
                    expr.expr()
                ),
                [
                    self.build_expr(Location.FromContext(px, self.stream), px)
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
                self.build_expr(Location.FromContext(lhs, self.stream), lhs),
                self.build_expr(Location.FromContext(rhs, self.stream), rhs),
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
            raise Exception(
                f'Unknown expr type {type(expr)} ({expr.getText()})'
            )

    def build_code_block(self, location, code_block):
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
                    code.append(
                        self.build_expr(
                            Location.FromContext(x, self.stream), x
                        )
                    )
            else:
                raise Exception(f'Unknown code block child {c.getText()}')
        return code

    def build_function_from_type_literal(self, location, literal):
        # yapf: disable
        return types.Function(
            location,
            self.build_param_list_from_type_literal_pairs(
                literal.typeLiteralPairList()
            ),
            self.get_or_create_type_literal(
                Location.FromContext(literal.typeLiteral(), self.stream),
                literal.typeLiteral()
            ) if (hasattr(literal, 'typeLiteral')
                  and literal.typeLiteral()) else None,
            self.build_code_block(
                Location.FromContext(literal.codeBlock(), self.stream),
                literal.codeBlock()
            )
        )

    def build_param_list_from_type_literal_pairs(self, pairs):
        # yapf: disable
        return {
            param_name.getText(): self.get_or_create_type_literal(
                Location.FromContext(type_literal, self.stream),
                type_literal
            )
            for param_name, type_literal in zip(
                pairs.singleIdentifier(),
                pairs.typeLiteral()
            )
        }


    def build_cstruct_from_type_literal(self, location, literal):
        # [TODO] Check for duplicate fields
        cstruct = types.CStruct(
            location,
            self.build_param_list_from_type_literal_pairs(
                literal.typeLiteralPairList()
            ),
        )
        for field_type in cstruct.fields.values():
            if not isinstance(field_type, types.CPtr):
                continue
            if not isinstance(field_type.referenced_type, ast.DeferredLookup):
                continue
            if not field_type.value == literal.singleIdentifier():
                raise errors.UndefinedSymbol(
                    field_type.location,
                    field_type.value
                )
            field_type.referenced_type = cstruct
        return cstruct

    def build_cunion_from_type_literal(self, location, literal):
        # [TODO] Check for duplicate fields
        return types.CUnion(
            location,
            self.build_param_list_from_type_literal_pairs(
                literal.typeLiteralPairList()
            ),
        )


    def build_cfunction_from_type_literal(self, location, literal):
        # yapf: disable
        return types.CFunction(
            location,
            self.build_param_list_from_type_literal_pairs(
                literal.typeLiteralPairList()
            ),
            self.get_or_create_type_literal(
                Location.FromContext(literal.typeLiteral(), self.stream),
                literal.typeLiteral()
            ) if (hasattr(literal, 'typeLiteral')
                  and literal.typeLiteral()) else None
        )


    def get_or_create_type_literal(self, location, literal, deferrable=False,
                                   modifier=TypeModifier.Raw):
        if isinstance(literal, types.SylvaType):
            # Already built it
            return literal
        if literal.carrayTypeLiteral():
            carray = literal.carrayTypeLiteral()
            element_count = (
                carray.intDecimalLiteral()
                if hasattr(carray, 'intDecimalLiteral')
                else None
            )
            if element_count is None:
                return types.CPtr(
                    location,
                    self.get_or_create_type_literal(
                        Location.FromContext(carray.typeLiteral(), self.stream),
                        carray.typeLiteral()
                    ),
                    referenced_type_is_mutable=True,
                    is_mutable=True,
                )
            return types.CArray(
                location,
                self.get_or_create_type_literal(
                    Location.FromContext(carray.typeLiteral(), self.stream),
                    carray.typeLiteral()
                ),
                int(element_count.getText())
            )
        if literal.cbitfieldTypeLiteral():
            cbitfield = literal.cbitfieldTypeLiteral()
            return types.CBitField(
                location,
                int(cbitfield.INT_TYPE().getText()[1:]),
                cbitfield.INT_TYPE().getText().startswith('i'),
                int(cbitfield.intDecimalLiteral().getText())
            )
        if literal.cblockfunctionTypeLiteral():
            cblockfntype = (
                literal.cblockfunctionTypeLiteral().functionTypeLiteral()
            )
            return types.CFunctionType(
                location,
                self.build_param_list_from_type_literal_pairs(
                    cblockfntype.typeLiteralPairList()
                ),
                self.get_or_create_type_literal(
                    Location.FromContext(
                        cblockfntype.typeLiteral(), self.stream
                    ),
                    cblockfntype.typeLiteral()
                ) if (hasattr(cblockfntype, 'typeLiteral')
                      and cblockfntype.typeLiteral()) else None
            )
        if literal.cfunctionTypeLiteral():
            cfntype = literal.cfunctionTypeLiteral().functionTypeLiteral()
            return types.CFunctionType(
                location,
                self.build_param_list_from_type_literal_pairs(
                    cfntype.typeLiteralPairList()
                ),
                self.get_or_create_type_literal(
                    Location.FromContext(cfntype.typeLiteral(), self.stream),
                    cfntype.typeLiteral()
                ) if (hasattr(cfntype, 'typeLiteral')
                      and cfntype.typeLiteral()) else None
            )
        if literal.cpointerTypeLiteral():
            text = literal.getText()
            referenced_type_is_mutable = False
            is_mutable = False

            if text.endswith('!'):
                is_mutable = True
                text = text[:-1]

            text = text[5:-1]

            if text.endswith('!'):
                referenced_type_is_mutable = True

            return types.CPtr(
                location,
                self.get_or_create_type_literal(
                    Location.FromContext(
                        literal.cpointerTypeLiteral().typeLiteral(),
                        self.stream
                    ),
                    literal.cpointerTypeLiteral().typeLiteral(),
                    deferrable=True
                ),
                referenced_type_is_mutable,
                is_mutable
            )
        if literal.cstructTypeLiteral():
            pass
        if literal.cunionTypeLiteral():
            pass
        if literal.cvoidTypeLiteral():
            return self.module.lookup('cvoid')
        if literal.arrayTypeLiteral():
            modifier = TypeModifier.FromTypeLiteral(literal)
        if literal.functionTypeLiteral():
            modifier = TypeModifier.FromTypeLiteral(literal)
        if literal.paramTypeLiteral():
            modifier = TypeModifier.FromTypeLiteral(literal)
        if literal.rangeTypeLiteral():
            modifier = TypeModifier.FromTypeLiteral(literal)
        if literal.structTypeLiteral():
            modifier = TypeModifier.FromTypeLiteral(literal)
        if literal.identifier():
            name = literal.getText()
            modifier = TypeModifier.FromTypeLiteral(literal)

            if modifier == TypeModifier.Pointer:
                name = name[1:]
            elif modifier == TypeModifier.Reference:
                name = name[1:]
            elif modifier == TypeModifier.ExclusiveReference:
                name = name[1:-1]

            value = self.module.lookup(name)

            if value is None:
                if deferrable:
                    debug('compile', f'Adding deferred type lookup for {name}')
                    return types.DeferredTypeLookup(
                        Location.FromContext(literal, self.stream),
                        name
                    )
                raise errors.UndefinedSymbol(location, name)

            return self.get_or_create_type_literal(
                location,
                value,
                modifier=modifier
            )

        raise Exception(f'Unknown type literal {literal.getText()}')

    def eval_const_literal(self, location, literal):
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


    def lookup_identifier(self, identifier):
        location = Location.FromContext(identifier, self.stream)
        name = identifier.getText()
        value = self.module.lookup(name)
        if value is None:
            raise errors.UndefinedSymbol(location, name)
        return value


    def exitAliasDef(self, ctx):
        if ctx.identifier():
            target = self.lookup_identifier(ctx.identifier())
        elif ctx.typeLiteral():
            target = self.get_or_create_type_literal(
                Location.FromContext(ctx.typeLiteral(), self.stream),
                ctx.typeLiteral()
            )
        else:
            raise Exception(f'Malformed alias def: {ctx.getText()}')
        self.module.add_alias(ctx.singleIdentifier().getText(), target)

    def exitConstDef(self, ctx):
        const_expr = ctx.constExpr()
        if const_expr.identifier():
            target = self.eval_const_literal(
                Location.FromContext(const_expr.identifier(), self.stream),
                self.lookup_identifier(const_expr.identifier())
            )
        elif const_expr.literal():
            target = self.eval_const_literal(
                Location.FromContext(const_expr.literal(), self.stream),
                const_expr.literal()
            )
        else:
            raise Exception(f'Malformed const def: {ctx.getText()}')
        self.module.define(ctx.singleIdentifier().getText(), target)

    def exitCfunctionTypeDef(self, ctx):
        self.module.define(
            ctx.singleIdentifier().getText(),
            self.build_cfunction_from_type_literal(
                Location.FromContext(ctx.functionTypeLiteral(), self.stream),
                ctx.functionTypeLiteral()
            )
        )

    def exitCunionTypeDef(self, ctx):
        self.module.define(
            ctx.singleIdentifier().getText(),
            self.build_cunion_from_type_literal(
                Location.FromContext(ctx, self.stream),
                ctx
            )
        )

    def exitCstructTypeDef(self, ctx):
        self.module.define(
            ctx.singleIdentifier().getText(),
            self.build_cstruct_from_type_literal(
                Location.FromContext(ctx, self.stream),
                ctx
            )
        )

    def exitFunctionDef(self, ctx):
        self.module.define(
            ctx.singleIdentifier().getText(),
            self.build_function_from_type_literal(
                Location.FromContext(ctx.functionLiteral(), self.stream),
                ctx.functionLiteral()
            )
        )
