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

# For backward compatibility
def visualize_chat_graph(root_node, output_file="chat_flowchart"):
    """Convenience function that creates a ChatVisualizer and calls visualize"""
    visualizer = ChatVisualizer()
    visualizer.visualize(root_node, output_file)