import enum

# pylint: disable=unused-import
from . import ast, debug, errors

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

    # pylint: disable=too-many-locals
    def build_expr(self, location, expr, local_type_lookup):
        debug('build_expr', f'build_expr {expr.getText()}')
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
                return ast.BooleanLiteralExpr.FromRawValue(
                    location, literal.getText()
                )
            elif literal.decimalLiteral():
                return ast.DecimalLiteralExpr.FromRawValue(
                    location, literal.getText()
                )
            elif literal.floatLiteral():
                return ast.FloatLiteralExpr.FromRawValue(
                    location, literal.getText()
                )
            elif literal.integerLiteral():
                return ast.IntegerLiteralExpr.FromRawValue(
                    location, literal.getText()
                )
            elif literal.runeLiteral():
                return ast.RuneLiteralExpr.FromRawValue(
                    location, literal.getText()
                )
            elif literal.stringLiteral():
                return ast.StringLiteralExpr.FromRawValue(
                    location, literal.getText()
                )
            else:
                raise Exception(
                    f'Unknown literal {literal} {literal.getText()}'
                )
        elif isinstance(expr, SylvaParser.ParenExprContext):
            pass
        elif isinstance(expr, SylvaParser.ArrayExprContext):
            pass
        elif isinstance(expr, SylvaParser.CArrayLiteralExprContext):
            pass
        elif isinstance(expr, SylvaParser.CPointerLiteralExprContext):
            # If there's a reference expr, we gotta unwrap it
            referenced_value = self.build_expr(
                Location.FromContext(expr.expr(), self.stream),
                expr.expr(),
                local_type_lookup,
            )

            if isinstance(referenced_value, ast.ReferencePointerExpr):
                referenced_value = referenced_value.referenced_value

            return ast.CPointerExpr.Build(
                location,
                referenced_value,
                expr.expr().children[-1].getText() == '!',
                expr.children[-1].getText() == '!',
                None
            )
        elif isinstance(expr, SylvaParser.CStructLiteralExprContext):
            pass
        elif isinstance(expr, SylvaParser.CUnionLiteralExprContext):
            pass
        elif isinstance(expr, SylvaParser.CVoidLiteralExprContext):
            location = Location.FromContext(expr.expr(), self.stream)
            return ast.CVoidCastExpr(
                location,
                self.build_expr(location, expr.expr(), local_type_lookup)
            )
        elif isinstance(expr, SylvaParser.SingleLookupExprContext):
            full_name = expr.getText()
            debug('lookup', f'SLookup: {full_name}')
            name = expr.singleIdentifier().getText()

            type = local_type_lookup.get(name)

            if type is None:
                value = self.module.lookup(location, name)
                if value is not None:
                    type = value.type

            if type is None:
                raise errors.UndefinedSymbol(location, name)

            lexpr = ast.LookupExpr(location, type, name)

            debug('lookup', f'SLookup: Got {lexpr}) from {full_name}')

            return lexpr

        elif isinstance(expr, SylvaParser.LookupExprContext):
            full_name = expr.getText()
            debug('lookup', f'Lookup: {full_name}')
            first_child = expr.children.pop(0)

            lexpr = self.build_expr(
                Location.FromContext(first_child, self.stream),
                first_child,
                local_type_lookup
            )

            # OK so this might be:
            # Dotting into a module
            # Dotting into a struct
            # Dotting into a cstruct
            # Dotting into a variant
            # Dotting into a cunion
            # Dotting into an enum
            # Dotting into an interface
            # Reflecting into a type
            # Reflecting into an instance

            debug(
                'lookup',
                f'Lookup: First child: {lexpr} (from {first_child.getText()})'
            )

            while expr.children:
                reflection = expr.children.pop(0).getText() == '::'
                field_name = expr.children.pop(0).getText()

                while isinstance(lexpr.type, ast.ConstDef):
                    debug('lookup', 'Following const def')
                    lexpr = lexpr.value

                if reflection:
                    debug('lookup', f'  Reflecting on {field_name} in {lexpr}')
                    field_type = lexpr.type.get_reflection_field_info(
                        field_name
                    )

                    if field_type is None:
                        raise errors.NoSuchField(location, field_name)

                    lexpr = ast.ReflectionLookupExpr(
                        location, field_type, lexpr.type, field_name
                    )
                elif isinstance(lexpr, ast.IndexedFieldsTypeDef):
                    debug('lookup', f'  Looking up {field_name} in {lexpr}')
                    res = lexpr.type.get_field_info(field_name)

                    if res is None:
                        raise errors.NoSuchField(location, field_name)

                    field_index, field_type = res

                    lexpr = ast.FieldIndexLookupExpr(
                        location, field_type, lexpr.type, field_index
                    )
                elif isinstance(lexpr, ast.NamedFieldsTypeDef):
                    res = lexpr.type.get_field_info(field_name)

                    if res is None:
                        raise errors.NoSuchField(location, field_name)

                    _, field_type = res

                    lexpr = ast.FieldNameLookupExpr(
                        location, field_type, lexpr.type, field_name
                    )
                elif isinstance(lexpr, ast.LookupExpr):
                    value = lexpr.type.lookup(location, field_name)
                    if value is None:
                        raise errors.NoSuchField(location, field_name)

                    while isinstance(value, ast.ConstDef):
                        debug('lookup', '  Following const def')
                        value = value.value

                    lexpr = ast.FieldNameLookupExpr(
                        location, value.type, lexpr.type, field_name
                    )
                else:
                    raise NotImplementedError()

                debug('lookup', f'  Got {lexpr} from {field_name}')

            debug('lookup', f'Lookup: Got {lexpr} from {full_name}')

            return lexpr

        elif isinstance(expr, SylvaParser.IndexExprContext):
            indexable_expr, index_expr = expr.expr()
            indexable = self.build_expr(
                Location.FromContext(indexable_expr, self.stream),
                indexable_expr,
                local_type_lookup
            )
            return ast.IndexExpr(
                location,
                indexable.element_type,
                indexable,
                self.build_expr(
                    Location.FromContext(index_expr, self.stream),
                    index_expr,
                    local_type_lookup
                )
            )
        elif isinstance(expr, SylvaParser.FunctionCallExprContext):
            function = self.build_expr(
                Location.FromContext(expr.expr(), self.stream),
                expr.expr(),
                local_type_lookup
            )
            return ast.CallExpr(
                location=location,
                type=function.type.return_type,
                function=function,
                arguments=[
                    self.build_expr(
                        Location.FromContext(px, self.stream),
                        px,
                        local_type_lookup
                    ) for px in expr.exprList().expr()
                ]
            )
        elif isinstance(expr, SylvaParser.ParamFunctionCallExprContext):
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
            return ast.MoveExpr(
                location,
                self.build_expr(
                    Location.FromContext(expr.expr()),
                    expr.expr(),
                    local_type_lookup
                ),
            )
        elif isinstance(expr, SylvaParser.ReferenceExprContext):
            return ast.ReferencePointerExpr(
                location=location,
                type=ast.ReferencePointerType(
                    location=location,
                    referenced_type=self.build_expr(
                        Location.FromContext(expr.expr()),
                        expr.expr(),
                        local_type_lookup
                    ),
                    is_exclusive=expr.children[-1].getText() == '!'
                ),
                name=None
            )
        else:
            raise Exception(
                f'Unknown expr type {type(expr)} ({expr.getText()})'
            )

    # pylint: disable=unused-argument
    def build_code_block(self, location, code_block, local_type_lookup):
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
                            Location.FromContext(x, self.stream),
                            x,
                            local_type_lookup
                        )
                    )
            else:
                raise Exception(f'Unknown code block child {c.getText()}')
        return code

    def build_param_list_from_type_literal_pairs(self, pairs):
        location = Location.FromContext(pairs, self.stream)

        return { # yapf: disable
            pn.getText(): self.get_or_create_type(location, tl)
            for pn, tl in zip(pairs.singleIdentifier(), pairs.typeLiteral())
        }

    def get_or_create_type(
        self, location, literal, deferrable=False, modifier=TypeModifier.Raw
    ):
        if literal.carrayTypeLiteral():
            carray = literal.carrayTypeLiteral()
            element_count = (
                carray.intDecimalLiteral()
                if hasattr(carray, 'intDecimalLiteral') else None
            )
            if element_count is None:
                return ast.CPtrType(
                    location=location,
                    referenced_type=self.get_or_create_type(
                        Location.FromContext(
                            carray.typeLiteral(), self.stream
                        ),
                        carray.typeLiteral()
                    ),
                    referenced_type_is_exclusive=True,
                    is_exclusive=True,
                )
            return ast.CArrayType(
                location=location,
                element_type=self.get_or_create_type(
                    Location.FromContext(carray.typeLiteral(), self.stream),
                    carray.typeLiteral()
                ),
                element_count=int(element_count.getText())
            )
        if literal.cbitfieldTypeLiteral():
            cbitfield = literal.cbitfieldTypeLiteral()
            return ast.CBitFieldType(
                int(cbitfield.INT_TYPE().getText()[1:]),
                cbitfield.INT_TYPE().getText().startswith('i'),
                int(cbitfield.intDecimalLiteral().getText())
            )
        if literal.cblockfunctionTypeLiteral():
            cblockfntype = (
                literal.cblockfunctionTypeLiteral().functionTypeLiteral()
            )
            return ast.CBlockFunctionPointerType(
                location=location,
                parameters=self.build_param_list_from_type_literal_pairs(
                    cblockfntype.typeLiteralPairList()
                ),
                return_type=self.get_or_create_type(
                    Location
                    .FromContext(cblockfntype.typeLiteral(), self.stream),
                    cblockfntype.typeLiteral()
                ) if (
                    hasattr(cblockfntype, 'typeLiteral') and
                    cblockfntype.typeLiteral()
                ) else None
            )
        if literal.cfunctionTypeLiteral():
            cfntype = literal.cfunctionTypeLiteral().functionTypeLiteral()
            return ast.CFunctionPointerType(
                location=location,
                parameters=self.build_param_list_from_type_literal_pairs(
                    cfntype.typeLiteralPairList()
                ),
                return_type=self.get_or_create_type( # yapf: disable
                    Location.FromContext(cfntype.typeLiteral(), self.stream),
                    cfntype.typeLiteral()
                ) if (hasattr(cfntype, 'typeLiteral') and
                     cfntype.typeLiteral()) else None
            )
        if literal.cpointerTypeLiteral():
            text = literal.getText()
            referenced_type_is_exclusive = False
            is_exclusive = False

            if text.endswith('!'):
                is_exclusive = True
                text = text[:-1]

            text = text[5:-1]

            if text.endswith('!'):
                referenced_type_is_exclusive = True

            return ast.CPtrType(
                location=location,
                referenced_type=self.get_or_create_type(
                    Location.FromContext(
                        literal.cpointerTypeLiteral().typeLiteral(),
                        self.stream
                    ),
                    literal.cpointerTypeLiteral().typeLiteral(),
                    deferrable=True
                ),
                referenced_type_is_exclusive=referenced_type_is_exclusive,
                is_exclusive=is_exclusive
            )
        if literal.cstructTypeLiteral():
            pass
        if literal.cunionTypeLiteral():
            pass
        if literal.cvoidTypeLiteral():
            return self.module.lookup(location, 'cvoid')
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

            # [TODO] Handle multiple dots/reflections

            type = self.module.lookup(location, name)

            debug('lookup', f'Got {type} from {name}')

            if type is None:
                if not deferrable:
                    raise errors.UndefinedSymbol(location, name)

                # [FIXME] This drops modifiers
                return ast.DeferredTypeLookup(
                    Location.FromContext(literal, self.stream), name
                )

            if isinstance(type, ast.TypeDef): # Already defined it
                type = type.type

            if isinstance(type, ast.SylvaType): # Already built it
                if modifier == TypeModifier.Pointer:
                    return ast.OwnedPointerType(location, type)
                if modifier == TypeModifier.Reference:
                    return ast.ReferencePointerType(
                        location, type, is_exclusive=False
                    )
                if modifier == TypeModifier.ExclusiveReference:
                    return ast.ReferencePointerType(
                        location, type, is_exclusive=True
                    )
                return type

            raise Exception(f'Unknown thing {type}')

        raise Exception(f'Unknown type literal {literal.getText()}')

    # pylint: disable=no-self-use
    def eval_const_literal(self, location, literal):
        if literal.arrayConstLiteral():
            pass
        elif literal.booleanLiteral():
            return ast.BooleanLiteralExpr.FromRawValue(
                location, literal.getText()
            )
        elif literal.decimalLiteral():
            return ast.DecimalLiteralExpr.FromRawValue(
                location, literal.getText()
            )
        elif literal.floatLiteral():
            return ast.FloatLiteralExpr.FromRawValue(
                location, literal.getText()
            )
        elif literal.functionLiteral():
            pass
        elif literal.integerLiteral():
            return ast.IntegerLiteralExpr.FromRawValue(
                location, literal.getText()
            )
        elif literal.rangeConstLiteral():
            pass
        elif literal.runeLiteral():
            return ast.RuneLiteralExpr.FromRawValue(
                location, literal.getText()
            )
        elif literal.stringLiteral():
            return ast.StringLiteralExpr.FromRawValue(
                location, literal.getText()
            )
        elif literal.structConstLiteral():
            pass

    def lookup_identifier(self, identifier):
        location = Location.FromContext(identifier, self.stream)
        name = identifier.getText()
        value = self.module.lookup(location, name)
        if value is None:
            raise errors.UndefinedSymbol(location, name)
        return value

    def exitAliasDef(self, ctx):
        if ctx.identifier():
            value = self.lookup_identifier(ctx.identifier())
        elif ctx.typeLiteral():
            value = self.get_or_create_type(
                Location.FromContext(ctx.typeLiteral(), self.stream),
                ctx.typeLiteral()
            )
        else:
            raise Exception(f'Malformed alias def: {ctx.getText()}')

        self.module.add_alias(
            ast.AliasDef(
                location=Location.FromContext(ctx, self.stream),
                name=ctx.singleIdentifier().getText(),
                value=value
            )
        )

    def exitConstDef(self, ctx):
        const_expr = ctx.constExpr()
        if const_expr.identifier():
            value = self.eval_const_literal(
                Location.FromContext(const_expr.identifier(), self.stream),
                self.lookup_identifier(const_expr.identifier())
            )
        elif const_expr.literal():
            value = self.eval_const_literal(
                Location.FromContext(const_expr.literal(), self.stream),
                const_expr.literal()
            )
        else:
            raise Exception(f'Malformed const def: {ctx.getText()}')

        # while isinstance(value, ast.ConstExpr):
        #     value = value.eval(location)

        self.module.add_definition(
            ast.ConstDef(
                location=Location.FromContext(ctx, self.stream),
                name=ctx.singleIdentifier().getText(),
                value=value
            )
        )

    def exitFunctionDef(self, ctx):
        func = ctx.functionLiteral()
        location = Location.FromContext(ctx, self.stream)
        name = ctx.singleIdentifier().getText()
        params = self.build_param_list_from_type_literal_pairs(
            func.typeLiteralPairList()
        )
        return_type = self.get_or_create_type( # yapf: disable
            Location.FromContext(func.typeLiteral(), self.stream),
            func.typeLiteral()
        ) if (hasattr(func, 'typeLiteral') and func.typeLiteral()) else None

        self.module.add_definition(
            ast.FunctionDef(
                location=location,
                name=name,
                type=ast.FunctionType(
                    location=location,
                    parameters=params,
                    return_type=return_type
                ),
                code=self.build_code_block(
                    Location.FromContext(func.codeBlock(), self.stream),
                    func.codeBlock(),
                    params
                )
            )
        )

    def exitCfunctionTypeDef(self, ctx):
        cfunc = ctx.functionTypeLiteral()
        name = ctx.singleIdentifier().getText()
        params = self.build_param_list_from_type_literal_pairs(
            cfunc.typeLiteralPairList()
        )
        return_type = self.get_or_create_type( # yapf: disable
            Location.FromContext(cfunc.typeLiteral(), self.stream),
            cfunc.typeLiteral()
        ) if (hasattr(cfunc, 'typeLiteral') and cfunc.typeLiteral()) else None

        location = Location.FromContext(ctx, self.stream)
        self.module.add_definition(
            ast.CFunctionDef(
                location=location,
                name=name,
                type=ast.CFunctionType(
                    location=location,
                    parameters=params,
                    return_type=return_type
                )
            )
        )

    def exitCunionTypeDef(self, ctx):
        location = Location.FromContext(ctx, self.stream)
        self.module.add_definition(
            ast.CUnionDef(
                location=location,
                name=ctx.singleIdentifier().getText(),
                type=ast.CUnionType(
                    location=location,
                    fields=self.build_param_list_from_type_literal_pairs(
                        ctx.typeLiteralPairList()
                    )
                )
            )
        )

    def exitCstructTypeDef(self, ctx):
        location = Location.FromContext(ctx, self.stream)
        name = ctx.singleIdentifier().getText()
        pairs = ctx.typeLiteralPairList()
        fields = self.build_param_list_from_type_literal_pairs(pairs)
        cstruct = ast.CStructType(location=location, name=name, fields=fields)

        for field_type in cstruct.fields.values():
            if not isinstance(field_type, ast.CPtrType):
                continue
            if not isinstance(field_type.referenced_type,
                              ast.DeferredTypeLookup):
                continue
            if not field_type.referenced_type.value == name:
                raise errors.UndefinedSymbol(
                    field_type.location, field_type.referenced_type.value
                )
            field_type.referenced_type = cstruct

        self.module.add_definition(
            ast.CStructDef(location=location, name=name, type=cstruct)
        )
