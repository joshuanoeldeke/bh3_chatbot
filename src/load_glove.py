import argparse
import pathlib
import urllib.request
import zipfile
import subprocess
import sys

# Import tqdm for progress bar (ignore unresolved import if not installed)
try:
    from tqdm import tqdm  # type: ignore
except ImportError:
    tqdm = None


def download_glove(url, zip_path):
    print(f"Downloading GloVe from {url} to {zip_path}...")
    response = urllib.request.urlopen(url)
    total = int(response.getheader('Content-Length').strip() or 0)
    with open(zip_path, 'wb') as out_file:
        with tqdm(total=total, unit='B', unit_scale=True, desc='Download') as pbar:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out_file.write(chunk)
                pbar.update(len(chunk))
    print("Download complete.")


def extract_glove(zip_path, members, dest_dir):
    print(f"Extracting GloVe files to {dest_dir}...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in members:
            print(f" - Extracting {member}")
            zf.extract(member, path=dest_dir)
    print("Extraction complete.")


def convert_to_word2vec(glove_path, output_path):
    print(f"Converting {glove_path.name} to Word2Vec format...")
    subprocess.run([
        sys.executable, '-m', 'gensim.scripts.glove2word2vec',
        '-i', str(glove_path), '-o', str(output_path)
    ], check=True)
    print(f"Saved converted file to {output_path.name}.")


def main():
    parser = argparse.ArgumentParser(
        description="Download and convert GloVe embeddings"
    )
    parser.add_argument('--version', default='6B',
                        help='GloVe version, e.g., 6B')
    parser.add_argument('--dims', nargs='+', type=int,
                        default=[50,100,200,300],
                        help='Embedding dimensions to process')
    parser.add_argument('--skip-download', action='store_true',
                        help="Skip downloading zip if present")
    parser.add_argument('--skip-extract', action='store_true',
                        help="Skip extracting files if present")
    parser.add_argument('--output-dir', type=pathlib.Path,
                        default=pathlib.Path(__file__).resolve().parents[1] / 'glove.6B',
                        help="Destination directory for embeddings")
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    project_root = output_dir.parent
    zip_url = f"https://nlp.stanford.edu/data/glove.{args.version}.zip"
    zip_path = project_root / f"glove.{args.version}.zip"

    # Download if necessary
    if not args.skip_download or not zip_path.exists():
        download_glove(zip_url, zip_path)
    else:
        print(f"Found existing zip at {zip_path.name}, skipping download.")

    # Extract selected dims if necessary
    if args.skip_extract:
        print("Skipping extraction of GloVe files.")
        return
    else:
        members = [f"glove.{args.version}.{dim}d.txt" for dim in args.dims]
        extract_glove(zip_path, members, output_dir)

    # Convert to Word2Vec format
    for dim in args.dims:
        glove_file = output_dir / f"glove.{args.version}.{dim}d.txt"
        w2v_file = output_dir / f"glove.{args.version}.{dim}d.w2v.txt"
        if w2v_file.exists():
            print(f"{w2v_file.name} already exists, skipping conversion.")
            continue
        convert_to_word2vec(glove_file, w2v_file)


if __name__ == '__main__':
    main()