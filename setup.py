#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil

# If all converted GloVe files exist, skip download to avoid large redownloads
def main():
    project_root = os.path.dirname(os.path.abspath(__file__))

    # --- Reinitialize SQLite database ---
    db_script = os.path.join(project_root, 'data', 'init_sqlite.py')
    print('Reinitializing SQLite database...')
    subprocess.run([sys.executable, db_script], check=True)

    # --- GloVe embeddings: skip download if already present ---
    glove_dir = os.path.join(project_root, 'glove.6B')
    dims = [50, 100, 200, 300]
    w2v_files = [os.path.join(glove_dir, f'glove.6B.{d}d.w2v.txt') for d in dims]
    if all(os.path.isfile(f) for f in w2v_files):
        print('GloVe embeddings already exist; skipping download and conversion.')
    else:
        # Remove any partial or old artifacts
        zip_path = os.path.join(project_root, 'glove.6B.zip')
        if os.path.exists(zip_path):
            print(f'Removing existing zip: {zip_path}')
            os.remove(zip_path)
        if os.path.isdir(glove_dir):
            print(f'Removing existing directory: {glove_dir}')
            shutil.rmtree(glove_dir)

        # Download and convert as usual
        print('Downloading and converting GloVe embeddings...')
        script = os.path.join(project_root, 'src', 'load_glove.py')
        subprocess.run([sys.executable, script], check=True)

    print('Setup complete.')

if __name__ == '__main__':
    main()