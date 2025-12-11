from flask import Flask, request, jsonify
import sqlite3
import uuid
import os

app = Flask(__name__)

# path database
DB_PATH = r'\\LAPTOP-8LH2FFMN\node_3_data\core.db'
# 
@app.route('/generate_tokens', methods=['POST'])

def generate():

    # menerima data berapa banyak token yang dibutuhkan
    data = request.json
    poll_id = data['poll_id']
    count = int(data['count'])
    
    # menampung link token
    links = []

    # membuka database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # looping mengulang sebanyak jumlah permintaan
    for _ in range(count):
        
        # membuat kode acak 8 karakter
        token = str(uuid.uuid4())[:8]

        # menyimpan ke database
        c.execute("INSERT INTO tokens (token_code, poll_id, is_used) VALUES (?, ?, 0)", (token, poll_id))
        
        # membuat link url token vote yang mengarah ke frontend
        links.append(f"http://localhost:5000/vote/{poll_id}?t={token}")
    
    # menutup & simpan ke frontend    
    conn.commit()
    conn.close()

    # mengembalikan daftar link ke frontend & ditampilkan
    return jsonify({"links": links})

# menyalakan server
if __name__ == '__main__':
    print("NODE 2 TOKEN")
    app.run(host='0.0.0.0',port=5005)