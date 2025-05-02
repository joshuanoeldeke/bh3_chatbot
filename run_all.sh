#!/usr/bin/env bash
set -e

echo "Starting Flask API on port 5000..."
python3 src/api/app.py &
API_PID=$!

echo "Starting Interactive Graph Editor on port 8050..."
python3 src/interactive.py &
EDITOR_PID=$!

echo "Starting Dash Chatbot UI on port 8051..."
python3 src/chat_ui.py &
CHAT_PID=$!

# Wait for all background processes
wait $API_PID $EDITOR_PID $CHAT_PID