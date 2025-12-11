from flask import Flask, jsonify
import sqlite3
import json
import os

app = Flask(__name__)

# path database
DB_PATH = r'\\LAPTOP-8LH2FFMN\node_3_data\core.db'


# fitur hapus
@app.route('/delete/<id_poll>', methods=['POST'])
def hapus_data(id_poll):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # hapus suara yang diinput user
        cur.execute("DELETE FROM votes WHERE poll_id=?", (id_poll,))
        
        # hapus token
        cur.execute("DELETE FROM tokens WHERE poll_id=?", (id_poll,))
        
        # hapus pertanyaan pollingnya
        cur.execute("DELETE FROM polls WHERE id=?", (id_poll,))
        
        conn.commit()
        conn.close()
        return jsonify({"status": "terhapus"})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# fitur riwayat
@app.route('/history', methods=['GET'])
def ambil_riwayat():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # ambil id dan soal dari yg terbaru
        cur.execute("SELECT id, question FROM polls ORDER BY id DESC")
        data = cur.fetchall()
        
        # dirapikan agar mudah dibaca frontend
        list_polling = [{'id': r[0], 'question': r[1]} for r in data]
        
        conn.close()
        return jsonify({"daftar_polling": list_polling})
    except Exception as e:
        # jika error, dikembalika list kosong agar ga crash
        return jsonify({"msg": str(e), "daftar_polling": []}), 500

# fitur melihat sisa token
@app.route('/tokens/<id_poll>', methods=['GET'])
def cek_token(id_poll):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT token_code FROM tokens WHERE poll_id=? AND is_used=0", (id_poll,))
        data = cur.fetchall()

        # membuat link lengkap tinggal copy
        link_jadi = [f"http://localhost:5000/vote/{id_poll}?t={x[0]}" for x in data]
        
        conn.close()
        return jsonify({"link_tersedia": link_jadi})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# fitur menghitung suara
@app.route('/summary/<id_poll>', methods=['GET'])
def hitung_suara(id_poll):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # mengambil detail soal & jawaban
        cur.execute("SELECT question, options FROM polls WHERE id=?", (id_poll,))
        data_soal = cur.fetchone()
        
        if not data_soal: return jsonify({"msg": "Polling hilang"}), 404
        
        soal = data_soal[0]
        pilihan = json.loads(data_soal[1]) # diubah jadi list

        # wadah hitungan
        hasil = {p: 0 for p in pilihan}
        
        # mengambil semua suara yang masuk
        cur.execute("SELECT choice_index FROM votes WHERE poll_id=?", (id_poll,))
        suara = cur.fetchall()
        
        # menghitung satu per satu
        for s in suara:
            idx = s[0] # index pilihan 0/1
            if 0 <= idx < len(pilihan):
                hasil[pilihan[idx]] += 1 # menambah 1
                
        conn.close()
        return jsonify({"soal": soal, "hasil": hasil})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# menyalakan server
if __name__ == '__main__':
    print("NODE 3 DATA RESULT")
    app.run(host='0.0.0.0', port=5004)