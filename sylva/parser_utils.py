from antlr4 import CommonTokenStream, ParseTreeWalker

from .lexer import SylvaLexer
from .parser import SylvaParser


def parse_with_listener(input_stream, listener):
    input_stream.reset()
    ParseTreeWalker().walk(
        listener,
        SylvaParser(CommonTokenStream(SylvaLexer(input_stream))).module()
    )
