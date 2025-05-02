from dash.dependencies import Input, Output, State
import dash
from .db import get_elements, get_node_options
from .constants import ADD_BTN_STYLE, UPDATE_BTN_STYLE, CANCEL_BTN_STYLE, HIDE_STYLE
import sqlite3

def register_callbacks(app, db_path):
    @app.callback(
        [Output('cytoscape', 'elements'),
         Output('edge-source', 'options'),
         Output('edge-target', 'options'),
         Output('callback-message', 'children')],
        [Input('add-node-button', 'n_clicks'),
         Input('add-edge-button', 'n_clicks'),
         Input('delete-node-button', 'n_clicks'),
         Input('delete-edge-button', 'n_clicks'),
         Input('update-node-button', 'n_clicks'),
         Input('update-edge-button', 'n_clicks'),
         Input('reset-graph-default', 'n_clicks')],
        [State('new-node-name', 'value'),
         State('new-node-content', 'value'),
         State('new-node-type', 'value'),
         State('edge-source', 'value'),
         State('edge-target', 'value'),
         State('cytoscape', 'selectedNodeData'),
         State('cytoscape', 'selectedEdgeData')]
    )
    def update_graph(n_node, n_edge, n_delete_node, n_delete_edge, n_update_node, n_update_edge, n_reset_graph, name, content, typ, src, tgt, sel_nodes, sel_edges):
        triggered = dash.callback_context.triggered
        msg = ''
        if not triggered:
            return get_elements(db_path), get_node_options(db_path), get_node_options(db_path), ''
        trigger_id = triggered[0]['prop_id'].split('.')[0]
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # Reset graph to default
        if trigger_id == 'reset-graph-default':
            try:
                c.execute("DELETE FROM chat_edges")
                c.execute("DELETE FROM chat_nodes")
                c.execute("INSERT INTO chat_nodes SELECT * FROM default_chat_nodes")
                c.execute("INSERT INTO chat_edges (from_name, to_name) SELECT from_name, to_name FROM default_chat_edges")
                conn.commit()
                msg = "Graph reset to default!"
            except Exception as e:
                msg = f"Error resetting graph: {e}"
            conn.close()
            elements = get_elements(db_path)
            opts = get_node_options(db_path)
            return elements, opts, opts, msg
        # Update node
        if trigger_id == 'update-node-button' and sel_nodes:
            old = sel_nodes[0]['id']
            c.execute("UPDATE chat_nodes SET content=?, type=? WHERE name=?", (content, typ, old))
            conn.commit()
            msg = f"Node '{old}' updated."
        # Update edge
        elif trigger_id == 'update-edge-button' and sel_edges:
            old_s = sel_edges[0]['source']; old_t = sel_edges[0]['target']
            c.execute("UPDATE chat_edges SET from_name=?, to_name=? WHERE from_name=? AND to_name=?", (src, tgt, old_s, old_t))
            conn.commit()
            msg = f"Edge '{old_s}->{old_t}' updated."
        # Add node
        elif trigger_id == 'add-node-button' and name and content and typ:
            try:
                c.execute("INSERT INTO chat_nodes (name, content, type) VALUES (?, ?, ?)", (name, content, typ))
                conn.commit()
                msg = f"Node '{name}' added."
            except Exception as e:
                msg = str(e)
        # Add edge
        elif trigger_id == 'add-edge-button' and src and tgt:
            try:
                c.execute("INSERT INTO chat_edges (from_name, to_name) VALUES (?, ?)", (src, tgt))
                conn.commit()
                msg = f"Edge '{src}' -> '{tgt}' added."
            except Exception as e:
                msg = str(e)
        # Delete selected nodes
        elif trigger_id == 'delete-node-button' and sel_nodes:
            for node in sel_nodes:
                nm = node.get('id')
                c.execute("DELETE FROM chat_edges WHERE from_name=? OR to_name=?", (nm, nm))
                c.execute("DELETE FROM chat_nodes WHERE name=?", (nm,))
            conn.commit()
            msg = f"Deleted nodes {[n.get('id') for n in sel_nodes]}."
        # Delete selected edges
        elif trigger_id == 'delete-edge-button' and sel_edges:
            for edge in sel_edges:
                s = edge.get('source'); t = edge.get('target')
                c.execute("DELETE FROM chat_edges WHERE from_name=? AND to_name=?", (s, t))
            conn.commit()
            msg = f"Deleted edges {[(e.get('source'), e.get('target')) for e in sel_edges]}."
        conn.close()
        # Refresh display
        elements = get_elements(db_path)
        opts = get_node_options(db_path)
        return elements, opts, opts, msg

    @app.callback(
        [Output('new-node-name','value'),
         Output('new-node-content','value'),
         Output('new-node-type','value'),
         Output('add-node-button','style'),
         Output('update-node-button','style'),
         Output('cancel-node-button','style'),
         Output('delete-node-button','style'),
         Output('cytoscape','selectedNodeData'),
         Output('edge-source','value'),
         Output('edge-target','value'),
         Output('add-edge-button','style'),
         Output('update-edge-button','style'),
         Output('cancel-edge-button','style'),
         Output('delete-edge-button','style'),
         Output('cytoscape','selectedEdgeData')],
        [Input('cytoscape','selectedNodeData'),
         Input('cancel-node-button','n_clicks'),
         Input('reset-node-default', 'n_clicks'),
         Input('cytoscape','selectedEdgeData'),
         Input('cancel-edge-button','n_clicks')],
        [State('cytoscape','selectedNodeData'),
         State('cytoscape','selectedEdgeData')],
        prevent_initial_call=False
    )
    def handle_node_edge_form(sel_node, cancel_node, reset_node, sel_edge, cancel_edge, sel_node_state, sel_edge_state):
        ctx = dash.callback_context
        # Defaults for all outputs
        node_defaults = ['', '', None, ADD_BTN_STYLE, HIDE_STYLE, HIDE_STYLE, HIDE_STYLE, [], None, None, ADD_BTN_STYLE, HIDE_STYLE, HIDE_STYLE, HIDE_STYLE, []]
        # Node logic
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('cancel-node-button'):
            return node_defaults
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('reset-node-default'):
            if sel_node_state and len(sel_node_state) == 1:
                node_name = sel_node_state[0]['id']
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("SELECT content, type FROM default_chat_nodes WHERE name=?", (node_name,))
                row = c.fetchone()
                conn.close()
                if row:
                    return [node_name, row[0], row[1], HIDE_STYLE, UPDATE_BTN_STYLE, CANCEL_BTN_STYLE, HIDE_STYLE, sel_node_state] + node_defaults[8:]
            return node_defaults
        if sel_node and len(sel_node)==1:
            node = sel_node[0]
            return [node['id'], node['label'], node.get('type'), HIDE_STYLE, UPDATE_BTN_STYLE, CANCEL_BTN_STYLE, {'display': 'inline-block'}, sel_node] + node_defaults[8:]
        # Edge logic
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('cancel-edge-button'):
            return node_defaults
        if sel_edge and len(sel_edge)==1:
            e = sel_edge[0]
            return node_defaults[:8] + [e['source'], e['target'], HIDE_STYLE, UPDATE_BTN_STYLE, CANCEL_BTN_STYLE, {'display': 'inline-block'}, sel_edge]
        # Default create mode
        return node_defaults

    @app.callback(
        [Output('cytoscape', 'stylesheet'),
         Output('cytoscape', 'layout')],
        [Input('node-width', 'value'),
         Input('node-height', 'value'),
         Input('font-size', 'value'),
         Input('node-sep', 'value'),
         Input('rank-sep', 'value'),
         Input('layout-dir', 'value')]
    )
    def update_cyto_style(node_width, node_height, font_size, node_sep, rank_sep, layout_dir):
        node_w = node_width if node_width != 120 else 'label'
        node_h = node_height if node_height != 60 else 'label'
        stylesheet=[
            {'selector': 'node', 'style': {
                'label': 'data(label)',
                'text-wrap': 'wrap',
                'text-valign': 'center',
                'text-halign': 'center',
                'width': node_w,
                'height': node_h,
                'background-color': '#eee',
                'font-size': f'{font_size}px',
                'padding': '12px',
                'shape': 'roundrectangle',
                'border-width': 2,
                'border-color': '#bbb',
                'min-zoomed-font-size': 10
            }},
            {'selector': '[type = "o"]', 'style': {'background-color': 'lightblue'}},
            {'selector': '[type = "i"]', 'style': {'background-color': 'lightyellow'}},
            {'selector': '[type = "c"]', 'style': {'background-color': 'lightgreen'}},
            {'selector': 'edge', 'style': {
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'arrow-scale': 1.2,
                'line-color': '#888',
                'width': 3
            }},
            {'selector': ':selected', 'style': {
                'background-color': '#fa0',
                'line-color': '#fa0',
                'border-color': '#fa0',
                'border-width': 4
            }}
        ]
        layout={
            'name': 'dagre',
            'nodeSep': node_sep,
            'edgeSep': 40,
            'rankSep': rank_sep,
            'rankDir': layout_dir
        }
        return stylesheet, layout

    @app.callback(
        [Output('add-node-button', 'className'), Output('add-node-button', 'disabled')],
        [Input('new-node-name', 'value'), Input('new-node-content', 'value'), Input('new-node-type', 'value'),
         Input('add-node-button', 'style'), Input('update-node-button', 'style')]
    )
    def set_add_node_btn_class(name, content, typ, add_style, update_style):
        if (add_style.get('display', 'inline-block') != 'none'):
            if all([name, content, typ]):
                return 'btn btn-primary w-100 mb-2', False
            else:
                return 'btn btn-secondary w-100 mb-2', True
        return 'btn btn-secondary w-100 mb-2', True

    @app.callback(
        [Output('add-edge-button', 'className'), Output('add-edge-button', 'disabled')],
        [Input('edge-source', 'value'), Input('edge-target', 'value'),
         Input('add-edge-button', 'style'), Input('update-edge-button', 'style')]
    )
    def set_add_edge_btn_class(src, tgt, add_style, update_style):
        if (add_style.get('display', 'inline-block') != 'none'):
            if src and tgt and src != tgt:
                return 'btn btn-primary w-100 mb-2', False
            else:
                return 'btn btn-secondary w-100 mb-2', True
        return 'btn btn-secondary w-100 mb-2', True

    @app.callback(
        [Output('update-node-button', 'className'), Output('update-node-button', 'disabled')],
        [Input('new-node-name', 'value'), Input('new-node-content', 'value'), Input('new-node-type', 'value'),
         Input('update-node-button', 'style')]
    )
    def set_update_node_btn_class(name, content, typ, update_style):
        if update_style.get('display', 'none') != 'none':
            if all([name, content, typ]):
                return 'btn btn-primary w-100 mb-2', False
            else:
                return 'btn btn-secondary w-100 mb-2', True
        return 'btn btn-secondary w-100 mb-2', True

    @app.callback(
        [Output('update-edge-button', 'className'), Output('update-edge-button', 'disabled')],
        [Input('edge-source', 'value'), Input('edge-target', 'value'),
         Input('update-edge-button', 'style')]
    )
    def set_update_edge_btn_class(src, tgt, update_style):
        if update_style.get('display', 'none') != 'none':
            if src and tgt:
                return 'btn btn-primary w-100 mb-2', False
            else:
                return 'btn btn-secondary w-100 mb-2', True
        return 'btn btn-secondary w-100 mb-2', True

    @app.callback(
        Output("settings-offcanvas", "is_open"),
        [Input("open-settings", "n_clicks")],
        [State("settings-offcanvas", "is_open")],
    )
    def toggle_settings(open_click, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open
        btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if btn_id == "open-settings":
            return True
        return is_open

    @app.callback(
        [Output('node-width', 'value'),
         Output('node-height', 'value'),
         Output('font-size', 'value'),
         Output('node-sep', 'value'),
         Output('rank-sep', 'value'),
         Output('layout-dir', 'value')],
        [Input('reset-settings', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_settings(n):
        return 120, 60, 15, 80, 120, 'LR'

    @app.callback(
        [Output('reset-node-default', 'style'), Output('reset-node-default', 'disabled')],
        [Input('cytoscape', 'selectedNodeData')]
    )
    def show_reset_node_btn(sel):
        if sel and len(sel) == 1:
            node_name = sel[0]['id']
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT 1 FROM default_chat_nodes WHERE name=?", (node_name,))
            exists = c.fetchone() is not None
            conn.close()
            if exists:
                return ({'display': 'inline-block'}, False)
            else:
                return ({'display': 'inline-block'}, True)
        return ({'display': 'none'}, True)
