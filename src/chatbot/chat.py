import os
import json
from .repliers import *
from .matchers import *
from .debug_mode import init_chat_log, log_chat

class Chat:
    def __init__(self, replier: Replier, matcher: Matcher):
        self.replier = replier
        self.matcher = matcher
        self.current_nodes = replier.get_start()
        self.log: list[ChatNode] = []
        # clear existing chat log storage
        init_chat_log()

        self.START = ""

    def advance(self, request: str) -> list[ChatNode]:
        # Use semantic matching if available, otherwise fallback to exact match
        try:
            node = self.matcher.semantic_match(request, self.current_nodes, default=self.START)
        except AttributeError:
            node = self.matcher.match(request, self.current_nodes, default=self.START)
        # record in both local and debug_mode store
        self.log.append(node)
        log_chat(node)

        # Insert request string to node if input
        if node.type == 'i': node.content = request

        self.current_nodes = self.replier.reply(node)
        return self.current_nodes
