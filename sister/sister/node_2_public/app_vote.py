from flask import Flask, request, jsonify
import sqlite3
from threading import Lock
from datetime import datetime
import os

app = Flask(__name__)
# path db
LOKASI_DB = os.path.join(os.path.dirname(__file__), '../node_3_data/core.db')

# ngunci agar tidak bentrok
gembok_db = Lock()

@app.route('/submit', methods=['POST'])
def terima_suara():
    data = request.json
    # ambil data dari frontend
    kode_token = data['token']
    id_poll = data['poll_id']
    pilihan = data['choice']
    
    # start antrian
    with gembok_db:
        try:
            conn = sqlite3.connect(LOKASI_DB)
            cur = conn.cursor()
            
            # Cek tokennya valid ga?
            cur.execute("SELECT is_used FROM tokens WHERE token_code=?", (kode_token,))
            baris = cur.fetchone()
            
            if not baris:
                conn.close()
                return jsonify({"msg": "token tidak dikenal"}), 403
            
            if baris[0] == 1:
                conn.close()
                return jsonify({"msg": "token tidak boleh sama"}), 403
                
            # simpan suara
            cur.execute("INSERT INTO votes (poll_id, choice_index, timestamp) VALUES (?, ?, ?)", 
                      (id_poll, pilihan, str(datetime.now())))
            
            # mematikan token agar tidak bisa dipake lagi
            cur.execute("UPDATE tokens SET is_used=1 WHERE token_code=?", (kode_token,))
            
            conn.commit()
            conn.close()
            return jsonify({"msg": "Suara masuk"}), 200
            
        except Exception as e:
            return jsonify({"msg": f"Gagal simpan: {str(e)}"}), 500

if __name__ == '__main__':
    print("NODE 2 VOTING")
    app.run(port=5003)