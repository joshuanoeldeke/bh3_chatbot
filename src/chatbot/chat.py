import os
import json
from .repliers import *
from .matchers import *

class Chat:
    def __init__(self, replier: Replier, matcher: Matcher):
        self.replier = replier
        self.matcher = matcher
        self.current_nodes = replier.get_start()
        self.log = []
        # prepare log directory and file path
        log_dir = os.environ.get('LOG_DIR', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = os.environ.get('CHAT_LOG_PATH', os.path.join(log_dir, 'chat_log.json'))
        # clear existing log file
        with open(self.log_path, 'w') as f:
            json.dump([], f, indent=2)

        self.START = ""

    def advance(self, request: str) -> list[ChatNode]:
        # Use semantic matching if available, otherwise fallback to exact match
        try:
            node = self.matcher.semantic_match(request, self.current_nodes, default=self.START)
        except AttributeError:
            node = self.matcher.match(request, self.current_nodes, default=self.START)
        self.log.append(node)
        # persist chat log to disk
        self._persist_log()

        # Insert request string to node if input
        if node.type == 'i': node.content = request

        self.current_nodes = self.replier.reply(node)
        return self.current_nodes
    
    def _persist_log(self):
        """Write the accumulated chat log as JSON to the log file"""
        data = [{'name': n.name, 'type': n.type, 'content': n.content} for n in self.log]
        with open(self.log_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
