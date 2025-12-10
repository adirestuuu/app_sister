from flask import Flask, request, jsonify
import sqlite3
from threading import Lock
from datetime import datetime
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '../node_3_data/core.db')
db_lock = Lock()

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    token = data['token']
    pid = data['poll_id']
    choice = data['choice']
    
    with db_lock:
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            c.execute("SELECT is_used FROM tokens WHERE token_code=?", (token,))
            row = c.fetchone()
            
            if not row:
                conn.close()
                return jsonify({"msg": "TOKEN TIDAK VALID"}), 403
            if row[0] == 1:
                conn.close()
                return jsonify({"msg": "ANDA SUDAH PERNAH VOTE SEBELUMNYA"}), 403
                
            c.execute("INSERT INTO votes (poll_id, choice_index, timestamp) VALUES (?, ?, ?)", 
                      (pid, choice, str(datetime.now())))
            c.execute("UPDATE tokens SET is_used=1 WHERE token_code=?", (token,))
            
            conn.commit()
            conn.close()
            return jsonify({"msg": "VOTE BERHASIL"}), 200
            
        except Exception as e:
            return jsonify({"msg": f"Error Database: {str(e)}"}), 500

if __name__ == '__main__':
    print("NODE 2 VOTE")
    app.run(port=5003)