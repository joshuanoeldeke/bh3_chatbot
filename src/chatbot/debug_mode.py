import os
import json
import builtins
import warnings


def is_debug():
    """Return True if debug mode is enabled."""
    return getattr(builtins, '_CHAT_DEBUG', False)


def debug_print(message):
    """Print a debug message if debug mode is enabled."""
    if is_debug():
        print(message)


def set_debug(flag: bool):
    """Enable or disable debug mode."""
    setattr(builtins, '_CHAT_DEBUG', flag)


def get_log_dir():
    """Ensure and return the directory for logs."""
    dir_path = os.environ.get('LOG_DIR', 'logs')
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def get_chat_log_path():
    """Return the path to the chat log file."""
    return os.environ.get('CHAT_LOG_PATH', os.path.join(get_log_dir(), 'chat_log.json'))


def init_chat_log():
    """Initialize (or clear) and return the chat log path."""
    path = get_chat_log_path()
    try:
        with open(path, 'w') as f:
            json.dump([], f, indent=2)
    except Exception as e:
        warnings.warn(f"Could not clear chat log file: {e}")
    _entries.clear()
    return path

def persist_chat_log(log, path=None):
    """Persist the given chat log list to disk."""
    if path is None:
        path = get_chat_log_path()
    try:
        with open(path, 'w') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
    except Exception as e:
        warnings.warn(f"Could not persist unified log: {e}")


def log_chat(node):
    """Append a ChatNode to in-memory log and persist to disk."""
    # record a chat entry in unified log
    entry = {'kind': 'chat', 'name': node.name, 'type': node.type, 'content': node.content}
    _entries.append(entry)
    persist_chat_log(_entries, get_chat_log_path())


def get_chat_log() -> list:
    """Return in-memory chat log entries."""
    return list(_entries)


def get_semantic_log_path():
    """Return the path to the semantic log file."""
    return os.environ.get('SEMANTIC_LOG_PATH', os.path.join(get_log_dir(), 'semantic_log.json'))


def init_semantic_log():
    """Initialize (or clear) and return the shared log path."""
    # use chat log path for unified storage
    path = get_chat_log_path()
    try:
        with open(path, 'w') as f:
            json.dump([], f, indent=2)
    except Exception as e:
        warnings.warn(f"Could not clear unified log file: {e}")
    _entries.clear()
    return path


def log_semantic(req, name, info):
    """Record a semantic match event in-memory and persist to disk."""
    # record a semantic entry in unified log
    entry = {'kind': 'semantic', 'req': req, 'name': name, 'info': info}
    _entries.append(entry)
    # persist using chat log path
    persist_chat_log(_entries, get_chat_log_path())
    debug_print(f"[LOG] '{req}' -> {name} ({info})")


def get_semantic_log() -> list:
    """Return in-memory semantic log entries (for backward compatibility)."""
    # filter unified entries for semantic ones
    return [e for e in _entries if e.get('kind') == 'semantic']


# In-memory log storage
_entries: list = []
