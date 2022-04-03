from antlr4 import *


class BaseSylvaLexer(Lexer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.templateDepth = 0

    @property
    def inTemplate(self):
        return self.templateDepth > 0

    def enterTemplate(self):
        self.templateDepth += 1

    def exitTemplate(self):
        if not self.inTemplate:
            raise Exception('Not in template')
        self.templateDepth -= 1
