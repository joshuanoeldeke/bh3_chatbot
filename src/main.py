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
current_prompt = None
current_nodes = None
should_advance = True

while True:
    # Only advance if we should - this is the key fix
    if should_advance:
        nodes = chat.advance(request)
        if not nodes:
            break
    else:
        # Re-use the current nodes without advancing
        nodes = current_nodes
        should_advance = True  # Reset flag for next iteration
    
    # Output node - just display it and continue
    if nodes[0].type == "o":
        print(f"Chatbot: {nodes[0].content}")
        current_prompt = None  # Reset prompt since we've advanced
    else:
        # If this is a new prompt (not a retry), save it
        if current_prompt is None:
            current_prompt = nodes[0].content
            current_nodes = nodes
        
        # Get user input
        user_input = chat_cli.input("You: ")
        
        # Check if input matches any of the available options
        matched = False
        for node in nodes:
            if node.type == "o":
                continue  # Skip output nodes
                
            keywords = node.content.split(";")
            if any(keyword.lower() in user_input.lower() for keyword in keywords if keyword):
                matched = True
                break
        
        # If no match, set flag to not advance and continue with same nodes
        if not matched:
            print("Chatbot: Ich habe das nicht verstanden. Bitte versuche es noch einmal.")
            should_advance = False
            request = ""  # Empty request 
            continue
        
        # Valid input, proceed normally
        request = user_input
        current_prompt = None
