#!/usr/bin/env python3
"""
Standalone script to visualize the chatbot conversation flow.
Run this script to generate a visualization of the chat graph without running the chatbot.
It uses Graphviz to create a flowchart of the conversation nodes and edges.
Usage:
    python visualize.py -o output_filename -f output_format -d database_path
    -o: Output filename (without extension)
    -f: Output file format (png, svg, pdf)
    -d: Path to the database file (defaults to ../data/bugland.db)
"""
import os
import sqlite3
import argparse
from chatbot import ChatNode
from chatbot.visualizer import ChatVisualizer

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
        db_path = os.path.join(os.path.dirname(__file__), "../data/bugland.db")
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return 1
    
    # Load conversation graph
    print("Loading conversation graph from database...")
    node_map = load_node_map(db_path)
    
    # Create visualization
    print("Generating visualization...")
    visualizer = ChatVisualizer(output_format=args.format)
    visualizer.visualize(node_map, output_file=args.output)
    
    return 0

if __name__ == "__main__":
    exit(main())