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
        # store the last question ChatNode for reprompting
        self._last_question_node: ChatNode = self.current_nodes[0] if self.current_nodes and self.current_nodes[0].type == 'o' else None
        # clear existing chat log storage
        init_chat_log()

        self.START = ""

    def advance(self, request: str) -> list[ChatNode]:
        # semantic or simple matching
        if hasattr(self.matcher, 'semantic_match'):
            node = self.matcher.semantic_match(request, self.current_nodes, default=self.START)
        else:
            node = self.matcher.match(request, self.current_nodes, default=self.START)
        # handle low-confidence reprompt
        if node is None and self._last_question_node:
            # apologize and reprompt
            apology = "Es tut mir leid, das habe ich leider nicht verstanden."
            print(f"Chatbot: {apology}")
            # return the same question; main() will print it once
            return [self._last_question_node]

        # record in both local and debug_mode store
        self.log.append(node)
        log_chat(node)

        # Insert request string to node if input
        if node.type == 'i': node.content = request

        self.current_nodes = self.replier.reply(node)
        # if next nodes start with a question, update last_question_node
        if self.current_nodes and self.current_nodes[0].type == 'o':
            self._last_question_node = self.current_nodes[0]
        return self.current_nodes
