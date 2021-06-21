from collections import namedtuple

from . import errors
from .lexer import Lexer
from .token import TokenType


ScannedItem = namedtuple('ScannedItem', ('location', 'name'))


class Scanner:

    token_type = None

    @staticmethod
    def lex_identifier(lexer):
        namespaces = []
        while True:
            token = lexer.lex()
            if not token.matches([TokenType.Value]):
                raise errors.UnexpectedTokenType(token, [TokenType.Value])
            namespaces.append(token.value)
            dot = lexer.get_next_if_matches([TokenType.AttributeLookup])
            if not dot:
                break
        return '.'.join(namespaces)

    @classmethod
    def scan(cls, data_source):
        scanned_items = []
        lexer = Lexer(data_source)
        for token in lexer:
            if not token.matches([cls.token_type]):
                continue
            scanned_items.append(ScannedItem(
                token.location.copy(),
                Scanner.lex_identifier(lexer)
            ))
        return scanned_items


class ModuleScanner(Scanner):

    token_type = TokenType.Module


class RequirementScanner(Scanner):

    token_type = TokenType.Requirement
