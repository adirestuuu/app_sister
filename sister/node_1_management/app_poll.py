from flask import Flask, request, jsonify
import requests
import sqlite3
import json
import os

app = Flask(__name__)

# path database
DB_PATH = r'\\LAPTOP-8LH2FFMN\node_3_data\core.db'

@app.route('/create', methods=['POST'])
def create():
    # menerima pertanyaan soal voting dari frontend
    data = request.json


    # sebelum soal dibuat, akan dihubungi api login
    try:

        # di cek apakah username dan passwordnya benar atau tidak dari api login (app_user)
        auth = requests.post('http://172.16.13.220/login', json={'username': 'admin', 'password': 'rahasia'}, timeout=2)

        # jika api login (app_user) statusnya bukan 200, akan ditolak
        if auth.status_code != 200:
            return jsonify({"Login ditolak"}), 401

    except:
        # jika api login (app_user) mati
        return jsonify({"msg": "API login mati"}), 503

    # menyimpan ke database
    try:
        # membuka database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # opsi pertanyaan diubah jadi teks biasa
        opts_str = json.dumps(data['options'])

        # memasukkan pertanyaan ke tabel
        c.execute("INSERT INTO polls (question, options) VALUES (?, ?)", (data['question'], opts_str))
        
        # mengambil id soal yang baru dibuat
        poll_id = c.lastrowid
        
        # menutup & simpan ke database
        conn.commit()
        conn.close()

        # di kembalikan ke frontend
        return jsonify({"poll_id": poll_id, "msg": "Poll Created"}), 201
    except Exception as e:

        # jika database error
        return jsonify({"msg": f"DB Error: {str(e)}"}), 500

# start server
if __name__ == '__main__':
    print("NODE 1 POLL PORT 5002")
    app.run(host='0.0.0.0', port=5002)