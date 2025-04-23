# BH3 Chatbot

A simple Python-based support chatbot for Bugland Ltd. that uses an SQLite database to store a conversation graph. The bot can answer user queries, guide through predefined flows, create support tickets, and collect feedback. This repository also includes a standalone visualization script to render the chat flow as a diagram.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Initialization](#database-initialization)
- [Project Structure](#project-structure)
- [Usage](#usage)
  - [Running the Chatbot](#running-the-chatbot)
  - [Visualizing the Chat Flow](#visualizing-the-chat-flow)
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

## Prerequisites

- Python 3.8 or newer
- pip (installed with Python)
- [Graphviz system package](https://graphviz.org/download/) (required by the Python `graphviz` module)

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
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── data/
│   ├── init.sql           # SQL schema and seed data
│   ├── init_sqlite.py     # Helper to build the DB
│   └── bugland.db         # Generated SQLite database
├── docs/
│   ├── chat_flowchart.png # Example chat flow visualization
│   └── use_case.*         # Use-case diagrams
├── src/
│   ├── main.py            # Entry point for CLI chatbot
│   ├── visualize.py       # Standalone chat flow visualizer
│   └── chatbot/           # Core chatbot package
│       ├── types.py       # ChatNode model
│       ├── chat.py        # Conversation engine
│       ├── matchers.py    # User input matching logic
│       ├── repliers.py    # Bot response resolver
│       ├── cli.py         # Console interface helpers
│       └── visualizer.py  # (Optional) separate visualizer module
└── tests/                 # Unit tests (pytest)
```

## Usage

### Running the Chatbot

```bash
cd src
python main.py
```

- **Optional visualization before starting**:
  ```bash
  python main.py --visualize
  ```
- Proceed through prompts in the terminal. The bot will ask questions, expect your input or choices, and may open tickets.

### Visualizing the Chat Flow

A standalone script generates a diagram of the entire conversation flow:

```bash
cd src
python visualize.py \
  --output chart_output \
  --format svg
```

- `--output`: Filename (without extension) for the generated diagram.
- `--format`: One of `png`, `svg`, or `pdf`.

The output file will be placed in the `docs/` directory by default.

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

This project is released under the MIT License. See [LICENSE](LICENSE) for details.