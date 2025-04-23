from .repliers import *
from .matchers import *

class Chat:
    def __init__(self, replier: Replier, matcher: Matcher):
        self.replier = replier
        self.matcher = matcher
        self.current_nodes = replier.get_start()
        self.log = []
        
        self.START = ""

    def advance(self, request: str) -> list[ChatNode]:
        # Use semantic matching if available, otherwise fallback to exact match
        try:
            node = self.matcher.semantic_match(request, self.current_nodes, default=self.START)
        except AttributeError:
            node = self.matcher.match(request, self.current_nodes, default=self.START)
        self.log.append(node)

        # Insert request string to node if input
        if node.type == 'i': node.content = request

        self.current_nodes = self.replier.reply(node)
        return self.current_nodes
