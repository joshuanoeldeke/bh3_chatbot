#!/usr/bin/env python3
import os, sys
from dash import Dash, dcc, html, Input, Output, State
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
    dcc.Store(id="history", data=[]),
    html.Div(id="chat-window", style={
        "border":"1px solid #ccc",
        "height":"400px", "overflowY":"auto", "padding":"10px", "marginBottom":"1rem"
    }),
    dbc.Row([
        dbc.Col(dcc.Input(id="user-input", type="text", placeholder="Type here…",
                          debounce=True, style={"width":"100%"}), width=10),
        dbc.Col(dbc.Button("Send", id="send-btn", color="primary"), width=2),
    ], align="center"),
    html.Div(id="suggestions", style={"marginTop":"0.5rem", "fontSize":"0.9em", "color":"#666"})
], fluid=True)

# --- callbacks ---

# -- on send: update history, advance chat_engine, clear input
@app.callback(
    Output("history",    "data"),
    Output("user-input", "value"),
    Input("send-btn",    "n_clicks"),
    State("user-input",  "value"),
    State("history",     "data"),
    prevent_initial_call=True
)
def on_send(n, text, history):
    if not text or not text.strip():
        return history, ""
    # record user
    history = history + [{"sender":"user", "text":text}]
    # advance bot
    next_nodes = chat_engine.advance(text)
    for n in next_nodes:
        history.append({"sender":"bot", "text": n.content})
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
    opts = []
    prefix = (text or "").lower()
    for node in chat_engine.current_nodes:
        key = node.content.split(";")[0]
        if not prefix or key.lower().startswith(prefix):
            opts.append(key)
    if not opts:
        return "no suggestions"
    return html.Span("Suggestions: " + ", ".join(opts))

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=8051)