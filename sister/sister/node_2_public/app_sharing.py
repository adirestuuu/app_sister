from flask import Flask, request, jsonify
import sqlite3
import uuid
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '../node_3_data/core.db')

@app.route('/generate_tokens', methods=['POST'])
def generate():
    data = request.json
    poll_id = data['poll_id']
    count = int(data['count'])
    
    links = []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for _ in range(count):
        token = str(uuid.uuid4())[:8] 
        c.execute("INSERT INTO tokens (token_code, poll_id, is_used) VALUES (?, ?, 0)", (token, poll_id))
        links.append(f"http://localhost:5000/vote/{poll_id}?t={token}")
        
    conn.commit()
    conn.close()
    return jsonify({"links": links})

if __name__ == '__main__':
    print("NODE 2 TOKEN")
    app.run(port=5005)