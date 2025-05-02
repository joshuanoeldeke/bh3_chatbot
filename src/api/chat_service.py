import os
import sys
# ensure parent directory is on path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from chatbot.chat import Chat
from chatbot.repliers import GraphReplier
from chatbot.matchers import StringMatcher
from visualize import load_node_map


def get_chat():
    # Determine database path from environment or default location
    db_path = os.environ.get('CHAT_DB_PATH')
    if not db_path:
        # Project root is two levels up from this file (src/api/chat_service.py)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        db_path = os.path.join(project_root, 'data', 'bugland.db')

    # Load graph and initialize Chat engine
    node_map = load_node_map(db_path)
    replier = GraphReplier(node_map.get('start'))
    matcher = StringMatcher()
    return Chat(replier, matcher)