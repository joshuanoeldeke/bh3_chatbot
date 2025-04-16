#!/usr/bin/env python3
"""
Standalone chat visualization script.
This script generates visualizations of the chatbot conversation flow.
"""
import os
import sqlite3
import argparse
import sys

# Add the src directory to the Python path if needed
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Add the docs directory to the Python path if needed
docs_dir = os.path.join(src_dir, "..", "docs")
if docs_dir not in sys.path:
    sys.path.append(docs_dir)

# We'll import ChatNode directly - do this before any chatbot module imports
# to avoid circular dependencies
from chatbot import ChatNode


class ChatVisualizer:
    """Class for visualizing chat graphs"""
    
    def __init__(self, output_format="png"):
        self.output_format = output_format
    
    def visualize(self, root_node, output_file="chat_flowchart"):
        """Generate a visual representation of the chat graph."""
        try:
            from graphviz import Digraph
            
            # Create a new directed graph
            dot = Digraph(comment='Chat Flow')
            
            # Function to recursively add nodes and edges
            def add_nodes_and_edges(node, visited=None):
                if visited is None:
                    visited = set()
                    
                if node.name in visited:
                    return
                
                visited.add(node.name)
                
                # Set node style based on type
                if node.type == "o":
                    # Output node (bot messages)
                    dot.node(node.name, f'"{node.content}"', shape='box', style='filled', fillcolor='lightblue')
                elif node.type == "i":
                    # Input node (user input fields)
                    dot.node(node.name, f'"{node.content}"', shape='parallelogram', style='filled', fillcolor='lightyellow')
                else:  # "c" for choice nodes
                    # Choice node (user selections)
                    dot.node(node.name, f'"{node.content}"', shape='oval', style='filled', fillcolor='lightgreen')
                
                # Add edges to children
                for child in node.children:
                    dot.edge(node.name, child.name)
                    add_nodes_and_edges(child, visited)
            
            # Check if we received a dictionary of nodes or a single root node
            if isinstance(root_node, dict):
                # Find the 'start' node as root
                if 'start' in root_node:
                    root = root_node['start']
                    add_nodes_and_edges(root)
                else:
                    # Process all nodes in the dictionary to ensure we cover the entire graph
                    for node in root_node.values():
                        add_nodes_and_edges(node)
            else:
                # Start with the single root node
                add_nodes_and_edges(root_node)
            
            # Render the graph
            dot.render(output_file, format=self.output_format, cleanup=True)
            print(f"Flowchart saved as {output_file}.{self.output_format}")
            
        except ImportError:
            print("Please install graphviz: pip install graphviz")
            print("You may also need to install the system Graphviz package.")


def visualize_chat_graph(root_node, output_file="chat_flowchart"):
    """Convenience function that creates a ChatVisualizer and calls visualize"""
    visualizer = ChatVisualizer()
    visualizer.visualize(root_node, output_file)


def load_node_map(db_path):
    """Load the conversation graph from the database."""
    node_map = {}
    
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
    return node_map


def main():
    """Entry point when run as a script"""
    parser = argparse.ArgumentParser(description='Generate a visualization of the chatbot conversation flow.')
    parser.add_argument('-o', '--output', default='chat_flowchart',
                       help='Output filename (without extension)')
    parser.add_argument('-f', '--format', default='png',
                       choices=['png', 'svg', 'pdf'],
                       help='Output file format')
    parser.add_argument('-d', '--database', default=None,
                       help='Path to the database file (defaults to ../data/bugland.db)')
    
    args = parser.parse_args()
    
    # Set database path
    if args.database:
        db_path = args.database
    else:
        # The script is in the src directory, so get the project root
        src_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(src_dir)
        db_path = os.path.join(project_root, "data/bugland.db")
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return 1
    
    # Load conversation graph
    print("Loading conversation graph from database...")
    node_map = load_node_map(db_path)
    
    # Set output path to docs directory
    output_path = os.path.join(docs_dir, args.output)

    # Create visualization
    print("Generating visualization...")
    visualizer = ChatVisualizer(output_format=args.format)
    visualizer.visualize(node_map, output_file=output_path)
    
    return 0


if __name__ == "__main__":
    exit(main())
