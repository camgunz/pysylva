class Scope:

    def __init__(self):
        self._scopes = [{}]

    def push(self):
        self._scopes.append({})

    def pop(self):
        if not self._scopes:
            raise Exception('No scopes to pop')
        self._scopes.pop(-1)

    def lookup(self, name):
        for scope in reversed(self._scopes):
            value = scope.get(name)
            if value:
                return value

    def define(self, name, value):
        # [TODO] Maybe warn about shadowing or something? Optionally?
        if not self._scopes:
            raise Exception('No scope to define a value in')
        self._scopes[-1][name] = value
