import os
import sqlite3
import argparse
import sys
import dash
from dash import html, dcc
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
cyto.load_extra_layouts()

# Button style constants for callbacks
ADD_BTN_STYLE = {'display':'inline-block', 'marginRight': '5px'}
UPDATE_BTN_STYLE = {'display':'inline-block', 'marginRight': '5px'}
CANCEL_BTN_STYLE = {'display':'inline-block'}
HIDE_STYLE = {'display':'none'}

def run_interactive(db_path, host='127.0.0.1', port=8050):
    """Launch Dash-based interactive graph editor."""
    # --- Data Helpers
    def get_elements():
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        nodes = c.execute("SELECT name, content, type FROM chat_nodes").fetchall()
        edges = c.execute("SELECT from_name, to_name FROM chat_edges").fetchall()
        conn.close()
        elements = []
        for name, content, typ in nodes:
            if typ == 'i' and (content is None or content.strip() == ''):
                label = 'User input required'
            else:
                label = content
            elements.append({'data': {'id': name, 'label': label, 'type': typ}})
        for src, tgt in edges:
            elements.append({'data': {'source': src, 'target': tgt}})
        return elements

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    # --- Layout Definition
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Interactive Chat Graph Editor"), width=10),
            dbc.Col(
                html.Button("⚙️ Settings", id="open-settings", className="btn btn-outline-secondary", style={"float": "right", "marginTop": "10px"}),
                width=2
            )
        ], className="mt-4 mb-2"),
        # Settings Offcanvas (sliding sidebar)
        dbc.Offcanvas([
            html.H5("Graph Display Settings"),
            dbc.Label("Node Width (all nodes)"),
            dcc.Slider(id='node-width', min=60, max=300, step=10, value=120, marks=None, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Node Height (all nodes)"),
            dcc.Slider(id='node-height', min=30, max=200, step=5, value=60, marks=None, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Font Size"),
            dcc.Slider(id='font-size', min=8, max=32, step=1, value=15, marks=None, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Horizontal Spacing (nodeSep)"),
            dcc.Slider(id='node-sep', min=20, max=300, step=10, value=80, marks=None, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Vertical Spacing (rankSep)"),
            dcc.Slider(id='rank-sep', min=40, max=400, step=10, value=120, marks=None, tooltip={"placement": "bottom", "always_visible": True}),
            dbc.Label("Layout Direction"),
            dcc.Dropdown(id='layout-dir', options=[
                {'label': 'Top to Bottom', 'value': 'TB'},
                {'label': 'Left to Right', 'value': 'LR'}
            ], value='LR', clearable=False, className='mb-2'),
        ], id="settings-offcanvas", title="Settings", is_open=False, placement="end", style={"width": "350px"}),
        dbc.Row([
            dbc.Col(
                cyto.Cytoscape(
                    id='cytoscape',
                    elements=get_elements(),
                    layout={
                        'name': 'dagre',
                        'nodeSep': 80,
                        'edgeSep': 40,
                        'rankSep': 120,
                        'rankDir': 'TB'
                    },
                    stylesheet=[
                        {'selector': 'node', 'style': {
                            'label': 'data(label)',
                            'text-wrap': 'wrap',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'width': 'label',  # dynamic sizing by default
                            'height': 'label',
                            'background-color': '#eee',
                            'font-size': '15px',
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
                    ],
                    style={'width': '100%', 'height': '600px'}
                ), width=12
            )
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Add Node"),
                dbc.CardBody([
                    dcc.Input(id='new-node-name', placeholder='Name', className='form-control mb-2'),
                    dcc.Input(id='new-node-content', placeholder='Content', className='form-control mb-2'),
                    dcc.Dropdown(id='new-node-type', options=[
                        {'label': 'Output (bot)', 'value': 'o'},
                        {'label': 'Input (user)', 'value': 'i'},
                        {'label': 'Choice', 'value': 'c'}
                    ], placeholder='Type', className='mb-2'),
                    html.Div([
                        html.Button('Add Node', id='add-node-button', className='btn btn-primary', style={'marginRight':'5px'}),
                        html.Button('Update Node', id='update-node-button', className='btn btn-secondary', style={'display':'none','marginRight':'5px'}),
                        html.Button('Cancel', id='cancel-node-button', className='btn btn-link', style={'display':'none'})
                    ])
                ])
            ]), md=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Add Edge"),
                dbc.CardBody([
                    dcc.Dropdown(id='edge-source', options=[], placeholder='Source', className='mb-2'),
                    dcc.Dropdown(id='edge-target', options=[], placeholder='Target', className='mb-2'),
                    html.Div([
                        html.Button('Add Edge', id='add-edge-button', className='btn btn-primary', style={'marginRight':'5px'}),
                        html.Button('Update Edge', id='update-edge-button', className='btn btn-secondary', style={'display':'none','marginRight':'5px'}),
                        html.Button('Cancel', id='cancel-edge-button', className='btn btn-link', style={'display':'none'})
                    ])
                ])
            ]), md=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Delete Selected"),
                dbc.CardBody([
                    html.Button('Delete Selected', id='delete-button', className='btn btn-danger')
                ])
            ]), md=4)
        ], className="mb-4"),
        dbc.Row(dbc.Col(html.Div(id='callback-message'), width=12))
    ], fluid=True)

    # --- Callback Definitions
    @app.callback(
        [Output('cytoscape', 'elements'),
         Output('edge-source', 'options'),
         Output('edge-target', 'options'),
         Output('callback-message', 'children')],
        [Input('add-node-button', 'n_clicks'),
         Input('add-edge-button', 'n_clicks'),
         Input('delete-button', 'n_clicks'),
         Input('update-node-button', 'n_clicks'),
         Input('update-edge-button', 'n_clicks')],
        [State('new-node-name', 'value'),
         State('new-node-content', 'value'),
         State('new-node-type', 'value'),
         State('edge-source', 'value'),
         State('edge-target', 'value'),
         State('cytoscape', 'selectedNodeData'),
         State('cytoscape', 'selectedEdgeData')]
    )
    def update_graph(n_node, n_edge, n_delete, n_update_node, n_update_edge, name, content, typ, src, tgt, sel_nodes, sel_edges):
        triggered = dash.callback_context.triggered
        msg = ''
        if not triggered:
            return get_elements(), get_node_options(), get_node_options(), ''
        trigger_id = triggered[0]['prop_id'].split('.')[0]
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
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
        # Delete selected nodes and/or edges
        elif trigger_id == 'delete-button':
            # Delete nodes
            if sel_nodes:
                for node in sel_nodes:
                    nm = node.get('id')
                    c.execute("DELETE FROM chat_edges WHERE from_name=? OR to_name=?", (nm, nm))
                    c.execute("DELETE FROM chat_nodes WHERE name=?", (nm,))
                conn.commit()
                msg = f"Deleted nodes {[n.get('id') for n in sel_nodes]}."
            # Delete edges
            if sel_edges:
                for edge in sel_edges:
                    s = edge.get('source'); t = edge.get('target')
                    c.execute("DELETE FROM chat_edges WHERE from_name=? AND to_name=?", (s, t))
                conn.commit()
                msg = (msg + ' ' if msg else '') + f"Deleted edges {[(e.get('source'), e.get('target')) for e in sel_edges]}."
        conn.close()
        # Refresh display
        elements = get_elements()
        opts = get_node_options()
        return elements, opts, opts, msg

    # Unified callback to manage node form (select, cancel)
    @app.callback(
        [Output('new-node-name','value'),
         Output('new-node-content','value'),
         Output('new-node-type','value'),
         Output('add-node-button','style'),
         Output('update-node-button','style'),
         Output('cancel-node-button','style'),
         Output('cytoscape','selectedNodeData')],
        [Input('cytoscape','selectedNodeData'),
         Input('cancel-node-button','n_clicks')]
    )
    def handle_node_form(sel, cancel_clicks):
        ctx = dash.callback_context
        # Cancel action
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('cancel-node-button'):
            return '', '', None, ADD_BTN_STYLE, HIDE_STYLE, HIDE_STYLE, []
        # Node selected
        if sel and len(sel)==1:
            node = sel[0]
            return node['id'], node['label'], node.get('type'), HIDE_STYLE, UPDATE_BTN_STYLE, CANCEL_BTN_STYLE, sel
        # Default create mode
        return '', '', None, ADD_BTN_STYLE, HIDE_STYLE, HIDE_STYLE, []

    # Unified callback to manage edge form (select, cancel)
    @app.callback(
        [Output('edge-source','value'),
         Output('edge-target','value'),
         Output('add-edge-button','style'),
         Output('update-edge-button','style'),
         Output('cancel-edge-button','style'),
         Output('cytoscape','selectedEdgeData')],
        [Input('cytoscape','selectedEdgeData'),
         Input('cancel-edge-button','n_clicks')]
    )
    def handle_edge_form(sel, cancel_clicks):
        ctx = dash.callback_context
        # Cancel action
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('cancel-edge-button'):
            return None, None, ADD_BTN_STYLE, HIDE_STYLE, HIDE_STYLE, []
        # Edge selected
        if sel and len(sel)==1:
            e = sel[0]
            return e['source'], e['target'], HIDE_STYLE, UPDATE_BTN_STYLE, CANCEL_BTN_STYLE, sel
        # Default create mode
        return None, None, ADD_BTN_STYLE, HIDE_STYLE, HIDE_STYLE, []
    
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
        # If user hasn't changed from default, use dynamic sizing
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

    # Settings menu open/close callbacks (offcanvas)
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

    def get_node_options():
        el = get_elements()
        nodes = [e['data']['id'] for e in el if 'source' not in e['data']]
        return [{'label': n, 'value': n} for n in nodes]

    app.run(host=host, port=port, debug=True)

if __name__ == "__main__":
    # The script is in the src directory, so get the project root
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    db_path = os.path.join(project_root, "data/bugland.db")
    run_interactive(db_path)