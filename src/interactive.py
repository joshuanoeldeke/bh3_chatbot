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

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css"])
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
            html.Button([
                html.I(className="bi bi-arrow-counterclockwise me-1"), "Reset to Default"
            ], id="reset-settings", className="btn btn-outline-warning w-100 mt-3"),
            html.Button([
                html.I(className="bi bi-arrow-clockwise me-1"), "Reset Graph to Default"
            ], id="reset-graph-default", className="btn btn-danger w-100 mt-2")
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
                dbc.CardHeader([
                    html.Span("Add Node", className="me-2"),
                    html.I(className="bi bi-plus-circle text-primary")
                ]),
                dbc.CardBody([
                    html.Div([
                        dbc.Label(["Node Name ",
                            html.I(className="bi bi-question-circle ms-1", id="help-node-name", style={"cursor": "pointer"})
                        ], html_for="new-node-name"),
                        dcc.Input(id='new-node-name', placeholder='Name', className='form-control mb-2'),
                        dbc.Tooltip("Unique identifier for the node.", target="help-node-name", placement="right")
                    ], className='mb-2'),
                    html.Div([
                        dbc.Label(["Node Content ",
                            html.I(className="bi bi-question-circle ms-1", id="help-node-content", style={"cursor": "pointer"})
                        ], html_for="new-node-content"),
                        dcc.Input(id='new-node-content', placeholder='Content', className='form-control mb-2'),
                        dbc.Tooltip("What the bot/user says or enters.", target="help-node-content", placement="right")
                    ], className='mb-2'),
                    html.Div([
                        dbc.Label(["Node Type ",
                            html.I(className="bi bi-question-circle ms-1", id="help-node-type", style={"cursor": "pointer"})
                        ], html_for="new-node-type"),
                        dcc.Dropdown(id='new-node-type', options=[
                            {'label': 'Output (bot)', 'value': 'o'},
                            {'label': 'Input (user)', 'value': 'i'},
                            {'label': 'Choice', 'value': 'c'}
                        ], placeholder='Type', className='mb-2'),
                        dbc.Tooltip("Choose the type of node.", target="help-node-type", placement="right")
                    ], className='mb-2'),
                    html.Div([
                        html.Button([
                            html.I(className="bi bi-plus-lg me-1"), "Add Node"
                        ], id='add-node-button', className='btn btn-secondary w-100 mb-2', disabled=True),
                        html.Button([
                            html.I(className="bi bi-pencil-square me-1"), "Update Node"
                        ], id='update-node-button', className='btn btn-primary w-100 mb-2', style={'display':'none'}),
                        html.Button([
                            html.I(className="bi bi-x-circle me-1"), "Cancel"
                        ], id='cancel-node-button', className='btn btn-link w-100', style={'display':'none'}),
                        html.Button([
                            html.I(className="bi bi-arrow-counterclockwise me-1"), "Reset to Default"
                        ], id='reset-node-default', className='btn btn-outline-warning w-100 mb-2', style={'display':'none'}, disabled=True),
                        html.Button([
                            html.I(className="bi bi-trash me-1"), "Delete Node"
                        ], id='delete-node-button', className='btn btn-danger w-100', style={'display':'none'})
                    ])
                ])
            ]), md=4, className="mb-3"),
            dbc.Col(dbc.Card([
                dbc.CardHeader([
                    html.Span("Add Edge", className="me-2"),
                    html.I(className="bi bi-arrow-right-circle text-primary")
                ]),
                dbc.CardBody([
                    html.Div([
                        dbc.Label(["Source Node ",
                            html.I(className="bi bi-question-circle ms-1", id="help-edge-source", style={"cursor": "pointer"})
                        ], html_for="edge-source"),
                        dcc.Dropdown(id='edge-source', options=[], placeholder='Source', className='mb-2'),
                        dbc.Tooltip("Start of the connection.", target="help-edge-source", placement="right")
                    ], className='mb-2'),
                    html.Div([
                        dbc.Label(["Target Node ",
                            html.I(className="bi bi-question-circle ms-1", id="help-edge-target", style={"cursor": "pointer"})
                        ], html_for="edge-target"),
                        dcc.Dropdown(id='edge-target', options=[], placeholder='Target', className='mb-2'),
                        dbc.Tooltip("End of the connection.", target="help-edge-target", placement="right")
                    ], className='mb-2'),
                    html.Div([
                        html.Button([
                            html.I(className="bi bi-plus-lg me-1"), "Add Edge"
                        ], id='add-edge-button', className='btn btn-secondary w-100 mb-2', disabled=True),
                        html.Button([
                            html.I(className="bi bi-pencil-square me-1"), "Update Edge"
                        ], id='update-edge-button', className='btn btn-primary w-100 mb-2', style={'display':'none'}),
                        html.Button([
                            html.I(className="bi bi-x-circle me-1"), "Cancel"
                        ], id='cancel-edge-button', className='btn btn-link w-100', style={'display':'none'}),
                        html.Button([
                            html.I(className="bi bi-trash me-1"), "Delete Edge"
                        ], id='delete-edge-button', className='btn btn-danger w-100', style={'display':'none'})
                    ])
                ])
            ]), md=4, className="mb-3"),
            dbc.Col(dbc.Card([
                dbc.CardHeader([
                    html.Span("Reset Graph to Default", className="me-2"),
                    html.I(className="bi bi-arrow-clockwise text-danger")
                ]),
                dbc.CardBody([
                    html.Button([
                        html.I(className="bi bi-arrow-clockwise me-1"), "Reset Graph to Default"
                    ], id="reset-graph-default", className="btn btn-danger w-100")
                ])
            ]), md=4, className="mb-3"),
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
            return get_elements(), get_node_options(), get_node_options(), ''
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
            elements = get_elements()
            opts = get_node_options()
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
        elements = get_elements()
        opts = get_node_options()
        return elements, opts, opts, msg

    # Unified callback to manage node form (select, cancel, reset-to-default)
    @app.callback(
        [Output('new-node-name','value'),
         Output('new-node-content','value'),
         Output('new-node-type','value'),
         Output('add-node-button','style'),
         Output('update-node-button','style'),
         Output('cancel-node-button','style'),
         Output('delete-node-button','style'),
         Output('cytoscape','selectedNodeData')],
        [Input('cytoscape','selectedNodeData'),
         Input('cancel-node-button','n_clicks'),
         Input('reset-node-default', 'n_clicks')],
        [State('cytoscape','selectedNodeData')],
        prevent_initial_call=False
    )
    def handle_node_form(sel, cancel_clicks, reset_clicks, sel_state):
        ctx = dash.callback_context
        # Cancel action
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('cancel-node-button'):
            return '', '', None, ADD_BTN_STYLE, HIDE_STYLE, HIDE_STYLE, HIDE_STYLE, []
        # Reset to default action
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('reset-node-default'):
            if sel_state and len(sel_state) == 1:
                node_name = sel_state[0]['id']
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("SELECT content, type FROM default_chat_nodes WHERE name=?", (node_name,))
                row = c.fetchone()
                conn.close()
                if row:
                    return node_name, row[0], row[1], HIDE_STYLE, UPDATE_BTN_STYLE, CANCEL_BTN_STYLE, HIDE_STYLE, sel_state
            # If no default, just keep current
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        # Node selected
        if sel and len(sel)==1:
            node = sel[0]
            return node['id'], node['label'], node.get('type'), HIDE_STYLE, UPDATE_BTN_STYLE, CANCEL_BTN_STYLE, {'display': 'inline-block'}, sel
        # Default create mode
        return '', '', None, ADD_BTN_STYLE, HIDE_STYLE, HIDE_STYLE, HIDE_STYLE, []

    # Unified callback to manage edge form (select, cancel)
    @app.callback(
        [Output('edge-source','value'),
         Output('edge-target','value'),
         Output('add-edge-button','style'),
         Output('update-edge-button','style'),
         Output('cancel-edge-button','style'),
         Output('delete-edge-button','style'),
         Output('cytoscape','selectedEdgeData')],
        [Input('cytoscape','selectedEdgeData'),
         Input('cancel-edge-button','n_clicks')]
    )
    def handle_edge_form(sel, cancel_clicks):
        ctx = dash.callback_context
        # Cancel action
        if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('cancel-edge-button'):
            return None, None, ADD_BTN_STYLE, HIDE_STYLE, HIDE_STYLE, HIDE_STYLE, []
        # Edge selected
        if sel and len(sel)==1:
            e = sel[0]
            return e['source'], e['target'], HIDE_STYLE, UPDATE_BTN_STYLE, CANCEL_BTN_STYLE, {'display': 'inline-block'}, sel
        # Default create mode
        return None, None, ADD_BTN_STYLE, HIDE_STYLE, HIDE_STYLE, HIDE_STYLE, []
    
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

    # Enable Add Node button only when all fields are filled
    @app.callback(
        [Output('add-node-button', 'className'), Output('add-node-button', 'disabled')],
        [Input('new-node-name', 'value'), Input('new-node-content', 'value'), Input('new-node-type', 'value'),
         Input('add-node-button', 'style'), Input('update-node-button', 'style')]
    )
    def set_add_node_btn_class(name, content, typ, add_style, update_style):
        # Only enable and color blue if all fields are filled and not in update mode
        if (add_style.get('display', 'inline-block') != 'none'):
            if all([name, content, typ]):
                return 'btn btn-primary w-100 mb-2', False
            else:
                return 'btn btn-secondary w-100 mb-2', True
        # In update mode, always keep add button grey and disabled
        return 'btn btn-secondary w-100 mb-2', True

    # Enable Add Edge button only when both fields are filled and source != target
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
        # In update mode, always keep add button grey and disabled
        return 'btn btn-secondary w-100 mb-2', True

    # Enable Update Node button only when all fields are filled and in update mode
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

    # Enable Update Edge button only when both fields are filled and in update mode
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
        # Defaults: width=120, height=60, font=15, nodeSep=80, rankSep=120, layoutDir='LR'
        return 120, 60, 15, 80, 120, 'LR'

    # Enable/disable and show/hide Reset to Default button for node
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