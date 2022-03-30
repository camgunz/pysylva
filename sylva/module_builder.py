from .listener import SylvaListener


class ModuleBuilder(SylvaListener):

    def __init__(self, module):
        self.module = module
