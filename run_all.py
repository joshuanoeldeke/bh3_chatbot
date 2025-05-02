#!/usr/bin/env python3
import subprocess
import sys
import time

# Define the services to run: (friendly name, command list)
services = [
    ('Flask API', ['python3', 'src/api/app.py']),
    ('Interactive Graph Editor', ['python3', 'src/interactive.py']),
    ('Dash Chatbot UI', ['python3', 'src/chat_ui.py']),
]

# Store subprocesses for cleanup
procs = []

def start_services():
    for name, cmd in services:
        print(f'Starting {name}...')
        # Launch each service in its own session to isolate SIGINT
        p = subprocess.Popen(cmd, start_new_session=True)
        procs.append(p)


def stop_services():
    print('\nShutting down services...')
    # First attempt graceful termination, then force kill if needed
    for p in procs:
        if p.poll() is None:
            try:
                p.terminate()
            except Exception:
                pass
    # Give processes a moment to exit
    time.sleep(1)
    # Force kill any that did not exit
    for p in procs:
        if p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass

if __name__ == '__main__':
    # Start all services
    start_services()
    # Keep running until user interrupts (Ctrl+C)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Clean up on Ctrl+C
        stop_services()
        sys.exit(0)