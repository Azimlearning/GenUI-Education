"""Typed node failures (TECHNICAL.md section 4: raise after one silent retry)."""


class NodeError(Exception):
    def __init__(self, node: str, message: str) -> None:
        self.node = node
        super().__init__(f"{node}: {message}")
