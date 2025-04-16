from abc import abstractmethod

from .types import *

class Matcher:
    @abstractmethod
    def match(self, request: str, nodes: list[ChatNode], default: str = "") -> ChatNode:
        pass

class StringMatcher(Matcher):
    """
    Simply finds the first choice explicitly mentioned in a request
    """
    def match(self, request: str, nodes: list[ChatNode], default: str = "") -> ChatNode:
        request = request.lower()
        for node in nodes:
            if node.type == "o":
                return node

            keywords = node.content.split(";")
            for word in keywords:
                if word.lower() in request:
                    return node
        return next((node for node in nodes if node.name == default), nodes[0])
