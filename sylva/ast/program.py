from dataclasses import dataclass

from sylva.ast.mod import Mod


@dataclass(kw_only=True)
class Program:
    modules: list[Mod]
