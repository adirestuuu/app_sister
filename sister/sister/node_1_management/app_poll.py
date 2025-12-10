from flask import Flask, request, jsonify
import requests
import sqlite3
import json
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '../node_3_data/core.db')

@app.route('/create', methods=['POST'])
def create():
    data = request.json
    try:
        auth = requests.post('http://localhost:5001/login', json={'username': 'admin', 'password': 'rahasia'}, timeout=2)
        if auth.status_code != 200:
            return jsonify({"msg": "Auth Ditolak"}), 401
    except:
        return jsonify({"msg": "Auth Service Mati"}), 503

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        opts_str = json.dumps(data['options'])
        c.execute("INSERT INTO polls (question, options) VALUES (?, ?)", (data['question'], opts_str))
        poll_id = c.lastrowid
        conn.commit()
        conn.close()
        return jsonify({"poll_id": poll_id, "msg": "Poll Created"}), 201
    except Exception as e:
        return jsonify({"msg": f"DB Error: {str(e)}"}), 500

if __name__ == '__main__':
    print("NODE 1")
    app.run(port=5002)