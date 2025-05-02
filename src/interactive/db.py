import sqlite3

def get_elements(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    nodes = c.execute("SELECT name, content, type FROM chat_nodes").fetchall()
    edges = c.execute("SELECT from_name, to_name FROM chat_edges").fetchall()
    conn.close()
    elements = []
    for name, content, typ in nodes:
        if typ == 'i' and (content is None or content.strip() == ''):
            label = 'User input required'
        else:
            label = content
        elements.append({'data': {'id': name, 'label': label, 'type': typ}})
    for src, tgt in edges:
        elements.append({'data': {'source': src, 'target': tgt}})
    return elements

def get_node_options(db_path):
    elements = get_elements(db_path)
    nodes = [e['data']['id'] for e in elements if 'source' not in e['data']]
    return [{'label': n, 'value': n} for n in nodes]
