from .repliers import *
from .matchers import *

class Chat:
    def __init__(self, replier: Replier, matcher: Matcher):
        self.replier = replier
        self.matcher = matcher
        self.current_nodes = replier.get_start()
        
        self.START = ""

    def advance(self, request: str) -> list[ChatNode]:
        node = self.matcher.match(request, self.current_nodes)

        # Insert request string to node if input
        if node.type == 'i': node.content = request

        self.current_nodes = self.replier.reply(node)
        return self.current_nodes
