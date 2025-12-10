from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '../node_3_data/core.db')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (data['username'], data['password']))
        user = c.fetchone()
        conn.close()
        
        if user:
            return jsonify({"status": "valid", "token": f"admin_session_{user[0]}"}), 200
        return jsonify({"status": "invalid", "msg": "Kredensial salah"}), 401
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == '__main__':
    print("NODE 1")
    app.run(port=5001)