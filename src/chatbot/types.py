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

class Reply:
    def __init__(self, msg: str, choices: list[str]):
        self.msg = msg
        self.choices = choices

    def __eq__(self, other: object) -> bool:
        if (isinstance(other, Reply)):
            return other.msg == self.msg
        else:
            return NotImplemented

    def __str__(self) -> str:
        return self.msg

class EmptyReply(Reply):
    def __init__(self):
        Reply.__init__(self, "", [])
