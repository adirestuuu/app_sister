from flask import Flask, jsonify
import sqlite3
import json
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'core.db')

# [BARU] Endpoint untuk ambil Riwayat Polling
@app.route('/history', methods=['GET'])
def history():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Ambil poll terbaru paling atas
        c.execute("SELECT id, question FROM polls ORDER BY id DESC")
        rows = c.fetchall()
        polls = [{'id': r[0], 'question': r[1]} for r in rows]
        conn.close()
        return jsonify({"polls": polls})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# [BARU] Endpoint untuk ambil Token yang Belum Dipakai (Satu Paket Link)
@app.route('/tokens/<poll_id>', methods=['GET'])
def get_tokens(poll_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT token_code FROM tokens WHERE poll_id=? AND is_used=0", (poll_id,))
        rows = c.fetchall()
        tokens = [f"http://localhost:5000/vote/{poll_id}?t={r[0]}" for r in rows]
        conn.close()
        return jsonify({"links": tokens})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/summary/<poll_id>', methods=['GET'])
def summary(poll_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT question, options FROM polls WHERE id=?", (poll_id,))
        poll = c.fetchone()
        
        if not poll: 
            return jsonify({"msg": "Poll not found"}), 404
        
        q_text = poll[0]
        opts = json.loads(poll[1])
        results = {opt: 0 for opt in opts}
        
        c.execute("SELECT choice_index FROM votes WHERE poll_id=?", (poll_id,))
        votes = c.fetchall()
        
        for v in votes:
            idx = v[0]
            if 0 <= idx < len(opts):
                results[opts[idx]] += 1
                
        conn.close()
        return jsonify({"soal": q_text, "hasil": results})
        
    except Exception as e:
        return jsonify({"msg": f"Error Node 3: {str(e)}"}), 500

if __name__ == '__main__':
    print("NODE 3 RESULT")
    app.run(port=5004)