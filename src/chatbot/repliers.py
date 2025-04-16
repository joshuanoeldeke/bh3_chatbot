from abc import abstractmethod

from .types import *

class Replier:
    """
    A replier takes a request and replies with a list of chatnodes.
    Either a list with one output chatnode is returned.
    Or a list with different choice chatnodes, upon which the user can choce one.
    """
    @abstractmethod
    def reply(self, request: ChatNode) -> list[ChatNode]:
        return []

    @abstractmethod
    def get_start(self) -> list[ChatNode]:
        return []

class HiReplier(Replier):
    def __init__(self) -> None:
        self.res = ChatNode("hi", "o", "Hi!")

    def reply(self, request: ChatNode) -> list[ChatNode]:
        if request.content == "ende":
            return []
        return [self.res]

    def get_start(self) -> list[ChatNode]:
        return [ChatNode("start", "o", "Hi!")]

class GraphReplier(Replier):
    def __init__(self, graph: ChatNode) -> None:
        self.graph = graph

    def reply(self, request: ChatNode) -> list[ChatNode]:
        return request.children

    def get_start(self) -> list[ChatNode]:
        # Add a root node that gets traversed on first call
        start = ChatNode("root", "", "")
        start.children = [self.graph]
        return [start]
