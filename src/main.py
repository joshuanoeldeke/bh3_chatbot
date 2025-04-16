import chatbot
from chatbot import ChatNode

import sqlite3
import os

# Import conversation graph
node_map: dict[str, ChatNode] = {}

db_path = os.path.join(os.path.dirname(__file__), "../data/bugland.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

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

conn.close()

# Let's use the graph for our chatbot
replier = chatbot.repliers.GraphReplier(node_map["start"])
matcher = chatbot.matchers.StringMatcher()
chat = chatbot.chat.Chat(replier, matcher)

# Helper CLI that adds tab-completion to reply choices provided by the chatbot
chat_cli = chatbot.Cli(chat)

request = chat.START

while (nodes := chat.advance(request)):
    match nodes[0].type:
        case "o":
            print(f"Chatbot: {nodes[0].content}")
        case _:
            request = chat_cli.input("You: ")

# Log the conversation
# Find the chat log in chat.log
