from flask import Flask, request, jsonify
import sqlite3
from threading import Lock # membuat antrian otomatis
from datetime import datetime
import os

app = Flask(__name__)

# lokasi database
DB_PATH = r'\\LAPTOP-8LH2FFMN\node_3_data\core.db'
# kunci agar tidak bentrok
kunci_db = Lock()

@app.route('/submit', methods=['POST'])
def terima_suara():
    # menangkap data yang dikirim dari frontend
    data = request.json
    kode_token = data['token']
    id_poll = data['poll_id']
    pilihan = data['choice']
    
    # menahan request lain & mencegah data bentrok
    with kunci_db:
        try:

            # membuka database
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # cek tokennya ada atau tidak
            cur.execute("SELECT is_used FROM tokens WHERE token_code=?", (kode_token,))
            baris = cur.fetchone()
            
            # jika token tidak dikenal
            if not baris:
                conn.close()
                return jsonify({"msg": "Token tidak dikenal"}), 403
            
            # jika sudah vote tapi tetap mau vote lagi
            if baris[0] == 1:
                conn.close()
                return jsonify({"msg": "Anda sudah melakukan voting sebelumnya"}), 403
                
            # mematikan token agar tidak dipakai lagi
            cur.execute("INSERT INTO votes (poll_id, choice_index, timestamp) VALUES (?, ?, ?)", 
                      (id_poll, pilihan, str(datetime.now())))
            
            # mematikan token agar tidak bisa dipake lagi
            cur.execute("UPDATE tokens SET is_used=1 WHERE token_code=?", (kode_token,))
            
            # simpan perubahan
            conn.commit()
            conn.close()
            return jsonify({"msg": "Suara masuk"}), 200
            
        except Exception as e:
            # jika ada eror
            return jsonify({"msg": f"Gagal simpan: {str(e)}"}), 500

# menyalakan server
if __name__ == '__main__':
    print("NODE 2 VOTING PORT 5003")
    app.run(host='0.0.0.0', port=5003)