#!/usr/bin/env python3
import os, sys
from dash import Dash, dcc, html, Input, Output, State, ALL, MATCH, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# ensure project src on path
src = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if src not in sys.path:
    sys.path.append(src)

from chatbot.chat import Chat
from chatbot.matchers import StringMatcher
from chatbot.repliers import GraphReplier
from visualize import load_node_map

# --- initialize Chat engine ---
project_root = os.path.dirname(src)
db_path       = os.path.join(project_root, "data", "bugland.db")
nodes         = load_node_map(db_path)
chat_engine   = Chat(GraphReplier(nodes["start"]), StringMatcher())

# --- Dash app setup ---
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    html.H2("Dash Chatbot UI"),
    dbc.Button("Reset", id="reset-btn", color="secondary", size="sm", style={"float":"right"}),
    dcc.Store(id="history", data=[]),
    dcc.Interval(id="init-interval", interval=1, n_intervals=0, max_intervals=1),
    html.Div(id="chat-window", style={
        "border":"1px solid #ccc",
        "height":"400px", "overflowY":"auto", "padding":"10px", "marginBottom":"1rem"
    }),
    dbc.Row([
        dbc.Col(dcc.Input(id="user-input", type="text", value="", placeholder="Type here…",
                          debounce=True, autoFocus=True, style={"width":"100%"}), width=10),
        dbc.Col(dbc.Button("Send", id="send-btn", color="primary"), width=2),
    ], align="center"),
    html.Div(id="suggestions", style={"marginTop":"0.5rem", "fontSize":"0.9em", "color":"#666"})
], fluid=True)

# --- callbacks ---

# unified callback for init, reset, send, submit, suggestion clicks
@app.callback(
    Output("history", "data"),
    Output("user-input", "value"),
    Input("init-interval", "n_intervals"),
    Input("send-btn", "n_clicks"),
    Input("user-input", "n_submit"),
    Input("reset-btn", "n_clicks"),
    Input({"type": "suggest", "value": ALL}, "n_clicks"),
    State("user-input", "value"),
    State("history", "data"),
    prevent_initial_call=False
)
def update_chat(init_n, send_clicks, submit, reset_clicks, suggest_clicks, text, history):
    triggered = ctx.triggered_id
    # initialize or reset: greet user
    if triggered == None or triggered == 'init-interval' or triggered == 'reset-btn':
        chat_engine.__init__(GraphReplier(nodes['start']), StringMatcher())
        node_list = chat_engine.advance("")
        return [{"sender":"bot","text":n.content} for n in node_list], ""
    # suggestion button click
    if isinstance(triggered, dict) and triggered.get('type') == 'suggest':
        text = triggered.get('value', '')
    # send or enter key
    if triggered in ('send-btn', 'user-input'):
        if not text or not text.strip():
            return history or [], ""
    # process user message
    history = (history or []) + [{"sender":"user","text":text}]
    next_nodes = chat_engine.advance(text)
    for n in next_nodes:
        history.append({"sender":"bot","text":n.content})
    return history, ""

# -- render chat window from history store
@app.callback(
    Output("chat-window", "children"),
    Input("history", "data")
)
def render_chat(h):
    elems = []
    for m in h:
        align = "right" if m["sender"]=="user" else "left"
        bg    = "#cce5ff" if m["sender"]=="user" else "#f1f1f1"
        elems.append(html.Div(m["text"], style={
            "textAlign": align,
            "background": bg,
            "padding":"0.5em","borderRadius":"5px","margin":"0.25em 0","maxWidth":"70%"
        }))
    return elems

# -- update suggestions on each keystroke
@app.callback(
    Output("suggestions", "children"),
    Input("user-input", "value")
)
def suggest(text):
    # Only show options from choice nodes
    opts = []
    prefix = (text or "").lower()
    for node in chat_engine.current_nodes:
        if node.type != 'c':
            continue
        # split multiple labels on semicolon
        for opt in node.content.split(';'):
            if not prefix or opt.lower().startswith(prefix):
                opts.append(opt)
    if not opts:
        return html.Div("no suggestions", style={"color":"#888"})
    # render clickable suggestion buttons
    buttons = []
    for opt in opts:
        btn_id = {'type': 'suggest', 'value': opt}
        buttons.append(
            dbc.Button(opt, id=btn_id, size="sm", color="secondary", className="me-1")
        )
    return html.Div(buttons)

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=8051)