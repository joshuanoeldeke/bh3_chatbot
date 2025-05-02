from interactive.app import run_interactive
import os

if __name__ == "__main__":
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    db_path = os.path.join(project_root, "data/bugland.db")
    run_interactive(db_path)