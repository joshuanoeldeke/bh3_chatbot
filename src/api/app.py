import os, sys
# ensure parent directory is on path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from chat_service import get_chat

# Initialize chat engine
chat = get_chat()

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """
    POST /chat
    Request JSON: {"message": "<user text>"}
    Response JSON: {"nodes": [{name,type,content}, ...]}
    """
    data = request.get_json(force=True)
    user_msg = data.get('message', '')

    # Advance conversation
    next_nodes = chat.advance(user_msg)

    # Serialize nodes
    nodes = [
        {"name": n.name, "type": n.type, "content": n.content}
        for n in next_nodes
    ]
    return jsonify(nodes=nodes)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
