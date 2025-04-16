from typing import Self

class ChatNode:
    def __init__(self, name: str, type: str, content: str) -> None:
        self.name = name
        self.type = type
        self.content = content
        self.children = []

    def addChild(self, child: Self) -> Self:
        self.children.append(child)
        return child
