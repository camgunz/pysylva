from antlr4 import *
from .parser import SylvaParser

# This class defines a complete listener for a parse tree produced by SylvaParser.
class SylvaParserListener(ParseTreeListener):

    # Enter a parse tree produced by SylvaParser#module.
    def enterModule(self, ctx:SylvaParser.ModuleContext):
        pass

    # Exit a parse tree produced by SylvaParser#module.
    def exitModule(self, ctx:SylvaParser.ModuleContext):
        pass


    # Enter a parse tree produced by SylvaParser#aliasDef.
    def enterAliasDef(self, ctx:SylvaParser.AliasDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#aliasDef.
    def exitAliasDef(self, ctx:SylvaParser.AliasDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#constDef.
    def enterConstDef(self, ctx:SylvaParser.ConstDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#constDef.
    def exitConstDef(self, ctx:SylvaParser.ConstDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#functionDef.
    def enterFunctionDef(self, ctx:SylvaParser.FunctionDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#functionDef.
    def exitFunctionDef(self, ctx:SylvaParser.FunctionDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#implementationDef.
    def enterImplementationDef(self, ctx:SylvaParser.ImplementationDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#implementationDef.
    def exitImplementationDef(self, ctx:SylvaParser.ImplementationDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#moduleDecl.
    def enterModuleDecl(self, ctx:SylvaParser.ModuleDeclContext):
        pass

    # Exit a parse tree produced by SylvaParser#moduleDecl.
    def exitModuleDecl(self, ctx:SylvaParser.ModuleDeclContext):
        pass


    # Enter a parse tree produced by SylvaParser#requirementDecl.
    def enterRequirementDecl(self, ctx:SylvaParser.RequirementDeclContext):
        pass

    # Exit a parse tree produced by SylvaParser#requirementDecl.
    def exitRequirementDecl(self, ctx:SylvaParser.RequirementDeclContext):
        pass


    # Enter a parse tree produced by SylvaParser#enumTypeDef.
    def enterEnumTypeDef(self, ctx:SylvaParser.EnumTypeDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#enumTypeDef.
    def exitEnumTypeDef(self, ctx:SylvaParser.EnumTypeDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#functionTypeDef.
    def enterFunctionTypeDef(self, ctx:SylvaParser.FunctionTypeDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#functionTypeDef.
    def exitFunctionTypeDef(self, ctx:SylvaParser.FunctionTypeDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#interfaceTypeDef.
    def enterInterfaceTypeDef(self, ctx:SylvaParser.InterfaceTypeDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#interfaceTypeDef.
    def exitInterfaceTypeDef(self, ctx:SylvaParser.InterfaceTypeDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#rangeTypeDef.
    def enterRangeTypeDef(self, ctx:SylvaParser.RangeTypeDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#rangeTypeDef.
    def exitRangeTypeDef(self, ctx:SylvaParser.RangeTypeDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#structTypeDef.
    def enterStructTypeDef(self, ctx:SylvaParser.StructTypeDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#structTypeDef.
    def exitStructTypeDef(self, ctx:SylvaParser.StructTypeDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#variantTypeDef.
    def enterVariantTypeDef(self, ctx:SylvaParser.VariantTypeDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#variantTypeDef.
    def exitVariantTypeDef(self, ctx:SylvaParser.VariantTypeDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#cblockfunctionTypeDef.
    def enterCblockfunctionTypeDef(self, ctx:SylvaParser.CblockfunctionTypeDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#cblockfunctionTypeDef.
    def exitCblockfunctionTypeDef(self, ctx:SylvaParser.CblockfunctionTypeDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#cfunctionTypeDef.
    def enterCfunctionTypeDef(self, ctx:SylvaParser.CfunctionTypeDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#cfunctionTypeDef.
    def exitCfunctionTypeDef(self, ctx:SylvaParser.CfunctionTypeDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#cstructTypeDef.
    def enterCstructTypeDef(self, ctx:SylvaParser.CstructTypeDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#cstructTypeDef.
    def exitCstructTypeDef(self, ctx:SylvaParser.CstructTypeDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#cunionTypeDef.
    def enterCunionTypeDef(self, ctx:SylvaParser.CunionTypeDefContext):
        pass

    # Exit a parse tree produced by SylvaParser#cunionTypeDef.
    def exitCunionTypeDef(self, ctx:SylvaParser.CunionTypeDefContext):
        pass


    # Enter a parse tree produced by SylvaParser#ifBlock.
    def enterIfBlock(self, ctx:SylvaParser.IfBlockContext):
        pass

    # Exit a parse tree produced by SylvaParser#ifBlock.
    def exitIfBlock(self, ctx:SylvaParser.IfBlockContext):
        pass


    # Enter a parse tree produced by SylvaParser#switchBlock.
    def enterSwitchBlock(self, ctx:SylvaParser.SwitchBlockContext):
        pass

    # Exit a parse tree produced by SylvaParser#switchBlock.
    def exitSwitchBlock(self, ctx:SylvaParser.SwitchBlockContext):
        pass


    # Enter a parse tree produced by SylvaParser#caseBlock.
    def enterCaseBlock(self, ctx:SylvaParser.CaseBlockContext):
        pass

    # Exit a parse tree produced by SylvaParser#caseBlock.
    def exitCaseBlock(self, ctx:SylvaParser.CaseBlockContext):
        pass


    # Enter a parse tree produced by SylvaParser#matchBlock.
    def enterMatchBlock(self, ctx:SylvaParser.MatchBlockContext):
        pass

    # Exit a parse tree produced by SylvaParser#matchBlock.
    def exitMatchBlock(self, ctx:SylvaParser.MatchBlockContext):
        pass


    # Enter a parse tree produced by SylvaParser#param.
    def enterParam(self, ctx:SylvaParser.ParamContext):
        pass

    # Exit a parse tree produced by SylvaParser#param.
    def exitParam(self, ctx:SylvaParser.ParamContext):
        pass


    # Enter a parse tree produced by SylvaParser#matchCaseBlock.
    def enterMatchCaseBlock(self, ctx:SylvaParser.MatchCaseBlockContext):
        pass

    # Exit a parse tree produced by SylvaParser#matchCaseBlock.
    def exitMatchCaseBlock(self, ctx:SylvaParser.MatchCaseBlockContext):
        pass


    # Enter a parse tree produced by SylvaParser#defaultBlock.
    def enterDefaultBlock(self, ctx:SylvaParser.DefaultBlockContext):
        pass

    # Exit a parse tree produced by SylvaParser#defaultBlock.
    def exitDefaultBlock(self, ctx:SylvaParser.DefaultBlockContext):
        pass


    # Enter a parse tree produced by SylvaParser#forBlock.
    def enterForBlock(self, ctx:SylvaParser.ForBlockContext):
        pass

    # Exit a parse tree produced by SylvaParser#forBlock.
    def exitForBlock(self, ctx:SylvaParser.ForBlockContext):
        pass


    # Enter a parse tree produced by SylvaParser#whileBlock.
    def enterWhileBlock(self, ctx:SylvaParser.WhileBlockContext):
        pass

    # Exit a parse tree produced by SylvaParser#whileBlock.
    def exitWhileBlock(self, ctx:SylvaParser.WhileBlockContext):
        pass


    # Enter a parse tree produced by SylvaParser#loopBlock.
    def enterLoopBlock(self, ctx:SylvaParser.LoopBlockContext):
        pass

    # Exit a parse tree produced by SylvaParser#loopBlock.
    def exitLoopBlock(self, ctx:SylvaParser.LoopBlockContext):
        pass


    # Enter a parse tree produced by SylvaParser#breakStmt.
    def enterBreakStmt(self, ctx:SylvaParser.BreakStmtContext):
        pass

    # Exit a parse tree produced by SylvaParser#breakStmt.
    def exitBreakStmt(self, ctx:SylvaParser.BreakStmtContext):
        pass


    # Enter a parse tree produced by SylvaParser#continueStmt.
    def enterContinueStmt(self, ctx:SylvaParser.ContinueStmtContext):
        pass

    # Exit a parse tree produced by SylvaParser#continueStmt.
    def exitContinueStmt(self, ctx:SylvaParser.ContinueStmtContext):
        pass


    # Enter a parse tree produced by SylvaParser#letStmt.
    def enterLetStmt(self, ctx:SylvaParser.LetStmtContext):
        pass

    # Exit a parse tree produced by SylvaParser#letStmt.
    def exitLetStmt(self, ctx:SylvaParser.LetStmtContext):
        pass


    # Enter a parse tree produced by SylvaParser#returnStmt.
    def enterReturnStmt(self, ctx:SylvaParser.ReturnStmtContext):
        pass

    # Exit a parse tree produced by SylvaParser#returnStmt.
    def exitReturnStmt(self, ctx:SylvaParser.ReturnStmtContext):
        pass


    # Enter a parse tree produced by SylvaParser#exprList.
    def enterExprList(self, ctx:SylvaParser.ExprListContext):
        pass

    # Exit a parse tree produced by SylvaParser#exprList.
    def exitExprList(self, ctx:SylvaParser.ExprListContext):
        pass


    # Enter a parse tree produced by SylvaParser#AndExpr.
    def enterAndExpr(self, ctx:SylvaParser.AndExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#AndExpr.
    def exitAndExpr(self, ctx:SylvaParser.AndExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#ReferenceExpr.
    def enterReferenceExpr(self, ctx:SylvaParser.ReferenceExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#ReferenceExpr.
    def exitReferenceExpr(self, ctx:SylvaParser.ReferenceExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#BandExpr.
    def enterBandExpr(self, ctx:SylvaParser.BandExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#BandExpr.
    def exitBandExpr(self, ctx:SylvaParser.BandExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#IndexExpr.
    def enterIndexExpr(self, ctx:SylvaParser.IndexExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#IndexExpr.
    def exitIndexExpr(self, ctx:SylvaParser.IndexExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#CPointerLiteralExpr.
    def enterCPointerLiteralExpr(self, ctx:SylvaParser.CPointerLiteralExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#CPointerLiteralExpr.
    def exitCPointerLiteralExpr(self, ctx:SylvaParser.CPointerLiteralExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#SingleLookupExpr.
    def enterSingleLookupExpr(self, ctx:SylvaParser.SingleLookupExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#SingleLookupExpr.
    def exitSingleLookupExpr(self, ctx:SylvaParser.SingleLookupExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#OwnedPointerExpr.
    def enterOwnedPointerExpr(self, ctx:SylvaParser.OwnedPointerExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#OwnedPointerExpr.
    def exitOwnedPointerExpr(self, ctx:SylvaParser.OwnedPointerExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#BorExpr.
    def enterBorExpr(self, ctx:SylvaParser.BorExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#BorExpr.
    def exitBorExpr(self, ctx:SylvaParser.BorExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#LiteralExpr.
    def enterLiteralExpr(self, ctx:SylvaParser.LiteralExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#LiteralExpr.
    def exitLiteralExpr(self, ctx:SylvaParser.LiteralExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#CUnionLiteralExpr.
    def enterCUnionLiteralExpr(self, ctx:SylvaParser.CUnionLiteralExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#CUnionLiteralExpr.
    def exitCUnionLiteralExpr(self, ctx:SylvaParser.CUnionLiteralExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#ShiftExpr.
    def enterShiftExpr(self, ctx:SylvaParser.ShiftExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#ShiftExpr.
    def exitShiftExpr(self, ctx:SylvaParser.ShiftExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#CArrayLiteralExpr.
    def enterCArrayLiteralExpr(self, ctx:SylvaParser.CArrayLiteralExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#CArrayLiteralExpr.
    def exitCArrayLiteralExpr(self, ctx:SylvaParser.CArrayLiteralExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#CVoidLiteralExpr.
    def enterCVoidLiteralExpr(self, ctx:SylvaParser.CVoidLiteralExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#CVoidLiteralExpr.
    def exitCVoidLiteralExpr(self, ctx:SylvaParser.CVoidLiteralExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#BxorExpr.
    def enterBxorExpr(self, ctx:SylvaParser.BxorExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#BxorExpr.
    def exitBxorExpr(self, ctx:SylvaParser.BxorExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#LookupExpr.
    def enterLookupExpr(self, ctx:SylvaParser.LookupExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#LookupExpr.
    def exitLookupExpr(self, ctx:SylvaParser.LookupExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#ParamFunctionCallExpr.
    def enterParamFunctionCallExpr(self, ctx:SylvaParser.ParamFunctionCallExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#ParamFunctionCallExpr.
    def exitParamFunctionCallExpr(self, ctx:SylvaParser.ParamFunctionCallExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#UnaryExpr.
    def enterUnaryExpr(self, ctx:SylvaParser.UnaryExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#UnaryExpr.
    def exitUnaryExpr(self, ctx:SylvaParser.UnaryExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#OrExpr.
    def enterOrExpr(self, ctx:SylvaParser.OrExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#OrExpr.
    def exitOrExpr(self, ctx:SylvaParser.OrExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#PowerExpr.
    def enterPowerExpr(self, ctx:SylvaParser.PowerExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#PowerExpr.
    def exitPowerExpr(self, ctx:SylvaParser.PowerExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#ArrayExpr.
    def enterArrayExpr(self, ctx:SylvaParser.ArrayExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#ArrayExpr.
    def exitArrayExpr(self, ctx:SylvaParser.ArrayExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#FunctionCallExpr.
    def enterFunctionCallExpr(self, ctx:SylvaParser.FunctionCallExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#FunctionCallExpr.
    def exitFunctionCallExpr(self, ctx:SylvaParser.FunctionCallExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#MulDivModExpr.
    def enterMulDivModExpr(self, ctx:SylvaParser.MulDivModExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#MulDivModExpr.
    def exitMulDivModExpr(self, ctx:SylvaParser.MulDivModExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#CmpExpr.
    def enterCmpExpr(self, ctx:SylvaParser.CmpExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#CmpExpr.
    def exitCmpExpr(self, ctx:SylvaParser.CmpExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#IncDecExpr.
    def enterIncDecExpr(self, ctx:SylvaParser.IncDecExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#IncDecExpr.
    def exitIncDecExpr(self, ctx:SylvaParser.IncDecExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#ParenExpr.
    def enterParenExpr(self, ctx:SylvaParser.ParenExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#ParenExpr.
    def exitParenExpr(self, ctx:SylvaParser.ParenExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#AddSubExpr.
    def enterAddSubExpr(self, ctx:SylvaParser.AddSubExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#AddSubExpr.
    def exitAddSubExpr(self, ctx:SylvaParser.AddSubExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#CStructLiteralExpr.
    def enterCStructLiteralExpr(self, ctx:SylvaParser.CStructLiteralExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#CStructLiteralExpr.
    def exitCStructLiteralExpr(self, ctx:SylvaParser.CStructLiteralExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#assignStmt.
    def enterAssignStmt(self, ctx:SylvaParser.AssignStmtContext):
        pass

    # Exit a parse tree produced by SylvaParser#assignStmt.
    def exitAssignStmt(self, ctx:SylvaParser.AssignStmtContext):
        pass


    # Enter a parse tree produced by SylvaParser#codeBlock.
    def enterCodeBlock(self, ctx:SylvaParser.CodeBlockContext):
        pass

    # Exit a parse tree produced by SylvaParser#codeBlock.
    def exitCodeBlock(self, ctx:SylvaParser.CodeBlockContext):
        pass


    # Enter a parse tree produced by SylvaParser#constExpr.
    def enterConstExpr(self, ctx:SylvaParser.ConstExprContext):
        pass

    # Exit a parse tree produced by SylvaParser#constExpr.
    def exitConstExpr(self, ctx:SylvaParser.ConstExprContext):
        pass


    # Enter a parse tree produced by SylvaParser#literal.
    def enterLiteral(self, ctx:SylvaParser.LiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#literal.
    def exitLiteral(self, ctx:SylvaParser.LiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#arrayConstLiteral.
    def enterArrayConstLiteral(self, ctx:SylvaParser.ArrayConstLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#arrayConstLiteral.
    def exitArrayConstLiteral(self, ctx:SylvaParser.ArrayConstLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#rangeConstLiteral.
    def enterRangeConstLiteral(self, ctx:SylvaParser.RangeConstLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#rangeConstLiteral.
    def exitRangeConstLiteral(self, ctx:SylvaParser.RangeConstLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#structConstLiteral.
    def enterStructConstLiteral(self, ctx:SylvaParser.StructConstLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#structConstLiteral.
    def exitStructConstLiteral(self, ctx:SylvaParser.StructConstLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#booleanLiteral.
    def enterBooleanLiteral(self, ctx:SylvaParser.BooleanLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#booleanLiteral.
    def exitBooleanLiteral(self, ctx:SylvaParser.BooleanLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#functionLiteral.
    def enterFunctionLiteral(self, ctx:SylvaParser.FunctionLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#functionLiteral.
    def exitFunctionLiteral(self, ctx:SylvaParser.FunctionLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#runeLiteral.
    def enterRuneLiteral(self, ctx:SylvaParser.RuneLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#runeLiteral.
    def exitRuneLiteral(self, ctx:SylvaParser.RuneLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#stringLiteral.
    def enterStringLiteral(self, ctx:SylvaParser.StringLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#stringLiteral.
    def exitStringLiteral(self, ctx:SylvaParser.StringLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#templateStringAtom.
    def enterTemplateStringAtom(self, ctx:SylvaParser.TemplateStringAtomContext):
        pass

    # Exit a parse tree produced by SylvaParser#templateStringAtom.
    def exitTemplateStringAtom(self, ctx:SylvaParser.TemplateStringAtomContext):
        pass


    # Enter a parse tree produced by SylvaParser#intDecimalLiteral.
    def enterIntDecimalLiteral(self, ctx:SylvaParser.IntDecimalLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#intDecimalLiteral.
    def exitIntDecimalLiteral(self, ctx:SylvaParser.IntDecimalLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#decimalLiteral.
    def enterDecimalLiteral(self, ctx:SylvaParser.DecimalLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#decimalLiteral.
    def exitDecimalLiteral(self, ctx:SylvaParser.DecimalLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#complexLiteral.
    def enterComplexLiteral(self, ctx:SylvaParser.ComplexLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#complexLiteral.
    def exitComplexLiteral(self, ctx:SylvaParser.ComplexLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#floatLiteral.
    def enterFloatLiteral(self, ctx:SylvaParser.FloatLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#floatLiteral.
    def exitFloatLiteral(self, ctx:SylvaParser.FloatLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#integerLiteral.
    def enterIntegerLiteral(self, ctx:SylvaParser.IntegerLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#integerLiteral.
    def exitIntegerLiteral(self, ctx:SylvaParser.IntegerLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#singleIdentifier.
    def enterSingleIdentifier(self, ctx:SylvaParser.SingleIdentifierContext):
        pass

    # Exit a parse tree produced by SylvaParser#singleIdentifier.
    def exitSingleIdentifier(self, ctx:SylvaParser.SingleIdentifierContext):
        pass


    # Enter a parse tree produced by SylvaParser#strictIdentifier.
    def enterStrictIdentifier(self, ctx:SylvaParser.StrictIdentifierContext):
        pass

    # Exit a parse tree produced by SylvaParser#strictIdentifier.
    def exitStrictIdentifier(self, ctx:SylvaParser.StrictIdentifierContext):
        pass


    # Enter a parse tree produced by SylvaParser#identifier.
    def enterIdentifier(self, ctx:SylvaParser.IdentifierContext):
        pass

    # Exit a parse tree produced by SylvaParser#identifier.
    def exitIdentifier(self, ctx:SylvaParser.IdentifierContext):
        pass


    # Enter a parse tree produced by SylvaParser#constExprList.
    def enterConstExprList(self, ctx:SylvaParser.ConstExprListContext):
        pass

    # Exit a parse tree produced by SylvaParser#constExprList.
    def exitConstExprList(self, ctx:SylvaParser.ConstExprListContext):
        pass


    # Enter a parse tree produced by SylvaParser#constExprPairList.
    def enterConstExprPairList(self, ctx:SylvaParser.ConstExprPairListContext):
        pass

    # Exit a parse tree produced by SylvaParser#constExprPairList.
    def exitConstExprPairList(self, ctx:SylvaParser.ConstExprPairListContext):
        pass


    # Enter a parse tree produced by SylvaParser#arrayTypeLiteral.
    def enterArrayTypeLiteral(self, ctx:SylvaParser.ArrayTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#arrayTypeLiteral.
    def exitArrayTypeLiteral(self, ctx:SylvaParser.ArrayTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#functionTypeLiteral.
    def enterFunctionTypeLiteral(self, ctx:SylvaParser.FunctionTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#functionTypeLiteral.
    def exitFunctionTypeLiteral(self, ctx:SylvaParser.FunctionTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#paramTypeLiteral.
    def enterParamTypeLiteral(self, ctx:SylvaParser.ParamTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#paramTypeLiteral.
    def exitParamTypeLiteral(self, ctx:SylvaParser.ParamTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#rangeTypeLiteral.
    def enterRangeTypeLiteral(self, ctx:SylvaParser.RangeTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#rangeTypeLiteral.
    def exitRangeTypeLiteral(self, ctx:SylvaParser.RangeTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#structTypeLiteral.
    def enterStructTypeLiteral(self, ctx:SylvaParser.StructTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#structTypeLiteral.
    def exitStructTypeLiteral(self, ctx:SylvaParser.StructTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#carrayTypeLiteral.
    def enterCarrayTypeLiteral(self, ctx:SylvaParser.CarrayTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#carrayTypeLiteral.
    def exitCarrayTypeLiteral(self, ctx:SylvaParser.CarrayTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#cbitfieldTypeLiteral.
    def enterCbitfieldTypeLiteral(self, ctx:SylvaParser.CbitfieldTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#cbitfieldTypeLiteral.
    def exitCbitfieldTypeLiteral(self, ctx:SylvaParser.CbitfieldTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#cblockfunctionTypeLiteral.
    def enterCblockfunctionTypeLiteral(self, ctx:SylvaParser.CblockfunctionTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#cblockfunctionTypeLiteral.
    def exitCblockfunctionTypeLiteral(self, ctx:SylvaParser.CblockfunctionTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#cfunctionTypeLiteral.
    def enterCfunctionTypeLiteral(self, ctx:SylvaParser.CfunctionTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#cfunctionTypeLiteral.
    def exitCfunctionTypeLiteral(self, ctx:SylvaParser.CfunctionTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#cstructTypeLiteral.
    def enterCstructTypeLiteral(self, ctx:SylvaParser.CstructTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#cstructTypeLiteral.
    def exitCstructTypeLiteral(self, ctx:SylvaParser.CstructTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#cunionTypeLiteral.
    def enterCunionTypeLiteral(self, ctx:SylvaParser.CunionTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#cunionTypeLiteral.
    def exitCunionTypeLiteral(self, ctx:SylvaParser.CunionTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#cpointerTypeLiteral.
    def enterCpointerTypeLiteral(self, ctx:SylvaParser.CpointerTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#cpointerTypeLiteral.
    def exitCpointerTypeLiteral(self, ctx:SylvaParser.CpointerTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#cvoidTypeLiteral.
    def enterCvoidTypeLiteral(self, ctx:SylvaParser.CvoidTypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#cvoidTypeLiteral.
    def exitCvoidTypeLiteral(self, ctx:SylvaParser.CvoidTypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#typeLiteral.
    def enterTypeLiteral(self, ctx:SylvaParser.TypeLiteralContext):
        pass

    # Exit a parse tree produced by SylvaParser#typeLiteral.
    def exitTypeLiteral(self, ctx:SylvaParser.TypeLiteralContext):
        pass


    # Enter a parse tree produced by SylvaParser#typeLiteralList.
    def enterTypeLiteralList(self, ctx:SylvaParser.TypeLiteralListContext):
        pass

    # Exit a parse tree produced by SylvaParser#typeLiteralList.
    def exitTypeLiteralList(self, ctx:SylvaParser.TypeLiteralListContext):
        pass


    # Enter a parse tree produced by SylvaParser#typeLiteralPairList.
    def enterTypeLiteralPairList(self, ctx:SylvaParser.TypeLiteralPairListContext):
        pass

    # Exit a parse tree produced by SylvaParser#typeLiteralPairList.
    def exitTypeLiteralPairList(self, ctx:SylvaParser.TypeLiteralPairListContext):
        pass


    # Enter a parse tree produced by SylvaParser#valueList.
    def enterValueList(self, ctx:SylvaParser.ValueListContext):
        pass

    # Exit a parse tree produced by SylvaParser#valueList.
    def exitValueList(self, ctx:SylvaParser.ValueListContext):
        pass



del SylvaParser