import os
import sys
from dash import Dash
from .layout import build_layout
import dash_bootstrap_components as dbc

# Ensure src is in sys.path for imports
src_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(src_dir)
if src_dir not in sys.path:
    sys.path.append(src_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

def run_interactive(db_path, host='127.0.0.1', port=8050):
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css"])
    app.layout = build_layout(db_path)
    # Import and register callbacks (they attach to app)
    from . import callbacks
    callbacks.register_callbacks(app, db_path)
    app.run(host=host, port=port, debug=True)
