import dash
from dash import html, dcc
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from .db import get_elements
from .constants import ADD_BTN_STYLE, UPDATE_BTN_STYLE, CANCEL_BTN_STYLE, HIDE_STYLE

cyto.load_extra_layouts()

def build_layout(db_path):
    return dbc.Container([
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
        ], id="settings-offcanvas", title="Settings", is_open=False, placement="end", style={"width": "350px"}),
        dbc.Row([
            dbc.Col(
                cyto.Cytoscape(
                    id='cytoscape',
                    elements=get_elements(db_path),
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
                            #'min-zoomed-font-size': 10
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
