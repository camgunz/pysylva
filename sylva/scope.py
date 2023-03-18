from dataclasses import dataclass, field
from typing import Any


@dataclass
class Scope:
    _scopes: list[dict] = field(default_factory=list)

    def push(self, scope: dict):
        self._scopes.append(scope)

    def pop(self):
        if not self._scopes:
            raise Exception('No scopes to pop')
        self._scopes.pop(-1)

    def lookup(self, name: str) -> Any:
        for scope in reversed(self._scopes):
            if value := scope.get(name):
                return value

    def define(self, name: str, value: Any):
        # [TODO] Maybe warn about shadowing or something? Optionally?
        if not self._scopes:
            raise Exception('No scope to define a value in')
        self._scopes[-1][name] = value
