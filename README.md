# BH3 Chatbot

A simple Python-based support chatbot for Bugland Ltd. that uses an SQLite database to store a conversation graph. The bot can answer user queries, guide through predefined flows, create support tickets, and collect feedback. This repository also includes a standalone visualization script to render the chat flow as a diagram.

## Table of Contents

- [Features](#features)
- [Detailed Functionality](#detailed-functionality)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Gensim and GloVe Embeddings](#gensim-and-glove-embeddings)
- [Database Initialization](#database-initialization)
- [Project Structure](#project-structure)
- [Usage](#usage)
  - [Interactive Graph Editor](#interactive-graph-editor)
  - [CLI Chatbot](#cli-chatbot)
  - [Web Chatbot UI (Flask + React)](#web-chatbot-ui-flask--react)
  - [Visualizing the Chat Flow](#visualizing-the-chat-flow)
  - [Running Tests](#running-tests)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

## Features

- Maintains a directed graph of chat nodes (messages, choices, and input fields) in SQLite.
- Dynamic flow logic driven by the database schema (`chat_nodes` and `chat_edges`).
- Supports:
  - Bot messages (`o` nodes)
  - User choice selections (`c` nodes)
  - Free-text input prompts (`i` nodes)
- Automatic ticket creation path with email capture.
- Feedback collection at the end of the conversation.
- Standalone visualization of the chat graph using Graphviz.

## Detailed Functionality

Below is a concise, step-by-step overview of the chatbot’s main components and how they work:

1. Conversation Graph
   - Stored in SQLite tables `chat_nodes` (node definitions) and `chat_edges` (directed links).
   - Each node has a `type`:
     - `o` = bot output (prompts or messages)
     - `c` = choice options (user picks one)
     - `i` = input fields (free-text entry)

2. Chat Engine (`chat.py`)
   - Manages the current set of available nodes and conversation history.
   - `advance(request)`:
     1. Calls the matcher to select the best next node for the user’s request.
     2. Appends the chosen node to an in-memory log and persists it to `logs/chat_log.json`.
     3. If it’s an input node (`i`), captures the user’s text in `node.content`.
     4. Asks the replier for the next child nodes and returns them.

3. Matching Logic (`matchers.py`)
   - `StringMatcher.match()`:
     • Simple literal or keyword matching against node contents.
   - `StringMatcher.semantic_match()` (8 steps):
     1. Exact keyword scan: longest keyword wins (fast fallback).
     2. Lazy-load GloVe embeddings from `GLOVE_MODEL_PATH` when first used.
     3. Preprocess both node content and user request (tokenize, lowercase, strip tags/URLs).
     4. Build a combined dictionary and TF–IDF corpus.
     5. Create a SoftCosine index using word embeddings for semantic similarity.
     6. Transform the user’s query into the TF–IDF vector space.
     7. Score against each node’s TF–IDF vector and pick the highest.
     8. Log the match and require a minimum score (0.1) or fallback.

4. Debug & Logging (`debug_mode.py`)
   - Central in-memory stores for both chat and semantic logs.
   - Clears logs on startup and writes JSON to `logs/chat_log.json` and `logs/semantic_log.json`.
   - Provides `set_debug()`, `is_debug()`, and `debug_print()` to control debug verbosity.
   - Exposes `get_chat_log()` and `get_semantic_log()` for post-mortem inspection.

All core functions are covered by unit tests (`pytest`) in `src/chatbot/*_test.py`.

## Prerequisites

- Python 3.11.8 (minimum)
- Recommended: Install and use pyenv to manage and pin Python versions. A `.python-version` file in the project root can specify `3.11.8` automatically for collaborators.
- pip (installed with Python)
- System dependencies:
  - macOS:
    - [Homebrew](https://brew.sh/)
    - pkg-config and OpenBLAS: `brew install pkg-config openblas`
    - Graphviz: `brew install graphviz`
  - Linux (Debian/Ubuntu):
    - pkg-config, OpenBLAS, Graphviz, and build tools: `sudo apt-get update && sudo apt-get install -y pkg-config libopenblas-dev graphviz build-essential`
  - Windows:
    - Graphviz: Download & install from https://graphviz.org/download/ and add to your PATH
    - Microsoft Visual C++ Build Tools: Install the "Desktop development with C++" workload from within [Visual Studio](https://visualstudio.microsoft.com/de/downloads/?q=build+tools) (required for native Python extensions)
- GloVe embeddings:
  - Download from [here](https://nlp.stanford.edu/projects/glove/)
  - Place the extracted files in the `glove.6B/` directory in the project root

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/bh3_chatbot.git
   cd bh3_chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate    # Windows
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Gensim and GloVe Embeddings

Gensim requires converting GloVe text files to Word2Vec format before loading them:

1. Ensure you have the GloVe files in `glove.6B/`.
2. Install gensim if not included: `pip install gensim`
3. Convert the embeddings using the built-in script:
   ```bash
   python -m gensim.scripts.glove2word2vec \
       -i glove.6B/glove.6B.100d.txt \
       -o glove.6B/glove.6B.100d.w2v.txt
   ```
4. Load the embeddings in your code:
   ```python
   from gensim.models import KeyedVectors
   model = KeyedVectors.load_word2vec_format(
       "glove.6B/glove.6B.100d.w2v.txt", binary=False
   )
   ```

## Problems with NLP Matching
- Since we are using a pre-trained GloVe model, the embeddings may not match the specific vocabulary of the chatbot.
- A work-around is to add specific keywords to the graph nodes to ensure they are matched correctly.
- The matcher will first check for exact matches before falling back to semantic matching.
- The matcher will also check for the longest keyword match first, so if you have a specific keyword that is longer than others, it will be matched first.

## Database Initialization

The conversation graph and ticket table are defined in `data/init.sql`. You can initialize the SQLite database in two ways:

- **Run the provided script**:
  ```bash
  python data/init_sqlite.py   # Generates `data/bugland.db` from `init.sql`
  ```

- **Manually via sqlite3 CLI**:
  ```bash
  sqlite3 data/bugland.db < data/init.sql
  ```

Ensure the file `data/bugland.db` exists before running the chatbot or visualization scripts.

## Project Structure

```
├── data/
│   ├── init.sql           # SQL schema and seed data
│   ├── init_sqlite.py     # Helper to build the DB
│   └── bugland.db         # Generated SQLite database
├── docs/
│   ├── activity.puml  # PUML for activity diagram
│   ├── activity.svg   # Example activity diagram
│   ├── chat_flowchart.png # Example chat flow visualization
│   ├── Chatbot-Konkurrenz_Alternativen.pdf # Chatbot alternatives
│   └── use_case.puml # PUML for use case diagram
│   └── use_case.SVG # example use case diagram
├── glove.6B/
│   ├── glove.6B.50d.txt   # GloVe embeddings (50d)
│   ├── glove.6B.50d.w2v.txt # GloVe embeddings (50d) in Word2Vec format
│   ├── glove.6B.100d.txt  # GloVe embeddings (100d)
│   ├── glove.6B.100d.w2v.txt # GloVe embeddings (100d) in Word2Vec format
│   ├── glove.6B.200d.txt  # GloVe embeddings (200d)
│   ├── glove.6B.200d.w2v.txt # GloVe embeddings (200d) in Word2Vec format
│   ├── glove.6B.300d.txt  # GloVe embeddings (300d)
│   ├── glove.6B.300d.w2v.txt # GloVe embeddings (300d) in Word2Vec format
├── logs/
│   ├── chat_log.json      # Chat history
├── src/
│   ├── load_glove.py      # GloVe embeddings loader
│   ├── main.py            # Entry point for CLI chatbot
│   ├── visualize.py       # Standalone chat flow visualizer
│   └── chatbot/           # Core chatbot package
│       ├── chat_test.py       # Pytest for chat engine
│       ├── chat.py        # Conversation engine
│       ├── cli_test.py     # Pytest for CLI
│       ├── cli.py         # CLI class
│       ├── debug_mode.py  # Debugging and logging
│       ├── matchers_test.py     # Pytest for matchers
│       ├── matchers.py     # Matcher classes
│       ├── repliers_test.py     # Pytest for repliers
│       ├── repliers.py     # Replier classes
│       ├── types_test.py  # Pytest for types
│       ├── types.py       # Node types
├── README.md              # This file
├── requirements.txt       # Python dependencies
```

## Usage

### Interactive Graph Editor

Launch the web-based editor to visually inspect and modify the conversation graph stored in SQLite.
```bash
python src/interactive.py
```
- Opens at http://127.th0.0.1:8050 by default.
- Click nodes or edges to edit their properties (content, type, connections).
- Use the form panel to Add, Update, or Delete nodes and edges.
- Graph styling: blue = bot output, yellow = user input, green = choice.
- Changes are persisted immediately to `data/bugland.db`.

### CLI Chatbot

Run the command‑line interface chatbot:
```bash
python src/main.py
```
- Add `--debug` to enable verbose logging.
- Use `--glove-dims <50|100|200|300>` to select an alternate GloVe model size.

### Visualizing the Chat Flow

A standalone script generates a diagram of the entire conversation flow:

```bash
cd src
python visualize.py --output chart_output --format svg
```
- `--output`: Filename (without extension) for the generated diagram.
- `--format`: One of `png`, `svg`, or `pdf`.

The output file will be placed in the `docs/` directory by default.

### Running Tests

This project uses `pytest`. To run all tests:
```bash
pytest
```

## Running Tests

This project uses `pytest`. To run all tests:

```bash
pytest
```

Tests cover:
- Chat engine logic (`chat_test.py`)
- Matchers, repliers, CLI behavior, and node parsing.

## Contributing

Contributions are welcome! Please:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -m 'Add my feature'`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Open a Pull Request.

Ensure all new code is covered by tests.

## License

This project is released under the MIT License.
