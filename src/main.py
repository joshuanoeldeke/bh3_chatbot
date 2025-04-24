import chatbot
from chatbot import ChatNode

import sqlite3
import os
import argparse

db_path = os.path.join(os.path.dirname(__file__), "../data/bugland.db")

# DB connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Function to open a ticket
def open_ticket(log: list[ChatNode], email: str) -> None:
    output = ""
    for node in log:
        if node.type == "i":
            output += node.name + ": " + node.content + "\n"

    cursor.execute("INSERT INTO tickets (content, email) VALUES (?, ?)", (output, email))

# Import conversation graph
node_map: dict[str, ChatNode] = {}

# Load all nodes
cursor.execute("SELECT name, content, type FROM chat_nodes")
rows = cursor.fetchall()

for name, content, typ in rows:
    node_map[name] = ChatNode(name, typ, content)

# Load all edges
cursor.execute("SELECT from_name, to_name FROM chat_edges")
edges = cursor.fetchall()

for from_name, to_name in edges:
    parent = node_map[from_name]
    child = node_map[to_name]
    parent.addChild(child)

# Let's use the graph for our chatbot
replier = chatbot.repliers.GraphReplier(node_map["start"])
matcher = chatbot.matchers.StringMatcher()
chat = chatbot.chat.Chat(replier, matcher)

# Helper CLI that adds tab-completion to reply choices provided by the chatbot
chat_cli = chatbot.Cli(chat)

# Disable tqdm progress bars globally
try:
    import tqdm
    tqdm.tqdm = lambda iterable=None, **kwargs: iterable if iterable is not None else []
    tqdm.trange = lambda *args, **kwargs: range(*args)
except ImportError:
    pass

if __name__ == "__main__":
    # Main CLI for chatbot with optional debug
    parser = argparse.ArgumentParser(description='Run chatbot with optional debug output')
    parser.add_argument('--debug', action='store_true', help='Enable debug output of path taken')
    parser.add_argument('--glove-dim', type=int, choices=[50,100,200,300], default=50,
                        help='Dimension of GloVe embeddings to load (50,100,200,300)')
    args, unknown = parser.parse_known_args()
    # Pass debug flag into environment
    import builtins
    builtins._CHAT_DEBUG = args.debug
    # Set GloVe model path relative to project root based on selected dimension
    import os, pathlib
    project_root = pathlib.Path(__file__).resolve().parents[1]
    glove_file = project_root / 'glove.6B' / f'glove.6B.{args.glove_dim}d.w2v.txt'
    os.environ['GLOVE_MODEL_PATH'] = str(glove_file)
    # Inform which GloVe model is loaded
    print(f"Using GloVe model: {glove_file.name}")

    request = chat.START

    # Print initial chatbot prompt
    for node in chat.current_nodes:
        if node.type == "o":
            print(f"Chatbot: {node.content}")

    while (nodes := chat.advance(request)):
        if args.debug:
            path = [node.name for node in chat.log]
            print("Path taken:", " -> ".join(path))
        match nodes[0].type:
            case "o":
                print(f"Chatbot: {nodes[0].content}")
            case _:
                request = chat_cli.input("You: ")

    # Find the chat log in chat.log
    for node in chat.log:
        if (node.name == "ticket_eroeffnen_email"):
            open_ticket(chat.log, node.content)

    conn.commit()
    conn.close()
    # Print semantic/exact match usage log
    if args.debug and hasattr(chat.matcher, 'semantic_log'):
        print("\n=== Match Usage Log ===")
        for req, node_name, score in chat.matcher.semantic_log:
            print(f"{req!r} -> {node_name} (score={score})")
