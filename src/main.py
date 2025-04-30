import argparse
import os
import pathlib
import sqlite3

from chatbot import ChatNode
from chatbot.debug_mode import *
from chatbot.repliers import GraphReplier
from chatbot.matchers import StringMatcher
from chatbot.chat import Chat
from chatbot.cli import Cli
from chatbot.debug_mode import get_semantic_log


def main():
    # Parse CLI args
    parser = argparse.ArgumentParser(description="Run chatbot with optional debug output")
    parser.add_argument("--debug", action="store_true", help="Enable debug output of path taken")
    parser.add_argument(
        "--glove-dim",
        type=int,
        choices=[50, 100, 200, 300],
        default=50,
        help="Dimension of GloVe embeddings to load",
    )
    args = parser.parse_args()

    # Set debug mode
    set_debug(args.debug)
    if args.debug:
        print("Debug mode enabled")

    # Disable tqdm bars if present
    try:
        import tqdm
        tqdm.tqdm = lambda it, **kw: it or []
        tqdm.trange = lambda *a, **kw: range(*a)
    except ImportError:
        pass

    # Configure GloVe model path
    project_root = pathlib.Path(__file__).resolve().parents[1]
    glove_file = project_root / "glove.6B" / f"glove.6B.{args.glove_dim}d.w2v.txt"
    os.environ["GLOVE_MODEL_PATH"] = str(glove_file)
    if args.debug:
        print(f"Using GloVe model: {glove_file.name}")

    # Connect to database
    db_path = project_root / "data" / "bugland.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    def open_ticket(log: list[ChatNode], email: str) -> None:
        content = "\n".join(f"{n.name}: {n.content}" for n in log if n.type == "i")
        cursor.execute(
            "INSERT INTO tickets (content, email) VALUES (?, ?)",
            (content, email),
        )

    # Load conversation graph
    cursor.execute("SELECT name, content, type FROM chat_nodes")
    rows = cursor.fetchall()
    node_map = {name: ChatNode(name, typ, content) for name, content, typ in rows}

    cursor.execute("SELECT from_name, to_name FROM chat_edges")
    for frm, to in cursor.fetchall():
        node_map[frm].addChild(node_map[to])

    # Initialize chatbot
    replier = GraphReplier(node_map["start"])
    matcher = StringMatcher()
    chat = Chat(replier, matcher)
    cli = Cli(chat)

    # Print initial prompt
    for n in chat.current_nodes:
        if n.type == "o":
            print(f"Chatbot: {n.content}")

    # Chat loop
    request = chat.START
    while (nodes := chat.advance(request)):
        if args.debug:
            path = " -> ".join(n.name for n in chat.log)
            print(f"Path taken: {path}")
        # Always print bot messages and then prompt user
        if nodes[0].type == "o":
            print(f"Chatbot: {nodes[0].content}")
        request = cli.input("You: ")

    # Handle ticket creation
    for n in chat.log:
        if n.name == "ticket_eroeffnen_email":
            open_ticket(chat.log, n.content)

    conn.commit()
    conn.close()

    # Always print the unified chat log
    from chatbot.debug_mode import get_chat_log
    entries = get_chat_log()
    if entries:
        print("\n=== Unified Chat Log ===")
        for entry in entries:
            print(entry)

    # Print semantic match usage log (debug only)
    # if args.debug:
    #     sem = get_semantic_log()
    #     if sem:
    #         print("\n=== Match Usage Log ===")
    #         for req, name, score in sem:
    #             print(f"{req!r} -> {name} ({score})")


if __name__ == "__main__":
    main()
