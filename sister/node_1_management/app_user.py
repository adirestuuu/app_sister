from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# lokasi database
DB_PATH = os.path.join(os.path.dirname(__file__), '../node_3_data/core.db')


# diaktifkan saat bagian frontend mengklik tombol "masuk"
@app.route('/login', methods=['POST'])

def login():
    # menerima username & password dari frontend
    data = request.json

    try:
        # membuka koneksi ke database di node_3_data
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        #mengecek tabel 'users' sesuai atau tidak user dengan username & password ini
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (data['username'], data['password']))
        user = c.fetchone() # diambil satu data jika ada

        # menutup koneksi
        conn.close()
        
        # logika
        if user:
            # jika datanya ketemu login sukses
            return jsonify({"status": "valid", "token": f"admin_session_{user[0]}"}), 200

        # jika datanya invalid login gagal
        return jsonify({"status": "invalid", "msg": "Username/Password Salah"}), 401

    except Exception as e:
        # jika ada error selain dua diatas
        return jsonify({"status": "error", "msg": str(e)}), 500


# menyalakan server
if __name__ == '__main__':
    print("NODE 1 MANAGEMENT PORT 5001")
    app.run(port=5001)