from flask import Flask, render_template_string, request, redirect, session, url_for
import requests

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_mahasiswa' 

# list alamat (node lain)
SERVER_AUTH = 'http://localhost:5001'
SERVER_SOAL = 'http://localhost:5002'
SERVER_VOTE = 'http://localhost:5003'
SERVER_DATA = 'http://localhost:5004'
SERVER_TOKEN = 'http://localhost:5005'

# interface
TAMPILAN_HTML = """
<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <title>E-Voting</title>
  <style>body { background-color: #f0f2f5; padding-top: 30px; }</style>
</head>
<body>
  <div class="container" style="max-width: 800px;">
    
    {% if notif %}
    <div class="alert {{ warna }} alert-dismissible fade show">
        {{ notif }} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    {% endif %}

    {% if halaman == 'login' %}
    <div class="card shadow-sm p-4 mx-auto" style="max-width: 400px;">
        <h3 class="text-center mb-4">Login</h3>
        <form action="/proses_login" method="POST">
            <div class="mb-3">
                <input name="user" class="form-control" value="admin" placeholder="Username">
            </div>
            <div class="mb-3">
                <input type="password" name="pass" class="form-control" value="rahasia" placeholder="Password">
            </div>
            <button class="btn btn-primary w-100">Kirim</button>
        </form>
    </div>
    {% endif %}

    {% if halaman == 'admin' %}
    <div class="card shadow-sm mb-4">
        <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <span class="fw-bold">Panel Kontrol</span>
            <a href="/logout" class="btn btn-light btn-sm text-primary fw-bold">Keluar</a>
        </div>
        <div class="card-body">
            <h5 class="card-title">Buat Polling Baru</h5>
            <form action="/buat_baru" method="POST">
                <input class="form-control mb-2" name="pertanyaan" placeholder="Taruh pertanyaan disini" required>
                <div class="row g-2 mb-2">
                    <div class="col"><input class="form-control" name="opsi_a" placeholder="Opsi 1" required></div>
                    <div class="col"><input class="form-control" name="opsi_b" placeholder="Opsi 2" required></div>
                </div>
                <input type="number" class="form-control mb-3" name="jumlah" value="3" placeholder="Jumlah Peserta">
                <button class="btn btn-success w-100">Kirim Pertanyaan</button>
            </form>
        </div>
    </div>

    <div class="card shadow-sm">
        <div class="card-header bg-secondary text-white">Daftar Polling Aktif</div>
        <div class="card-body p-0">
            <table class="table table-hover mb-0">
                <thead>
                    <tr>
                        <th class="ps-3">ID</th>
                        <th>Pertanyaan</th>
                        <th class="text-end pe-3">Aksi</th>
                    </tr>
                </thead>
                <tbody>
                {% if data_history %}
                    {% for item in data_history %}
                    <tr>
                        <td class="ps-3">#{{ item.id }}</td>
                        <td>{{ item.question }}</td>
                        <td class="text-end pe-3">
                            <a href="/lihat_token/{{ item.id }}" class="btn btn-sm btn-outline-primary">Token</a>
                            <a href="/lihat_grafik/{{ item.id }}" class="btn btn-sm btn-outline-warning">Aktivitas</a>
                            
                            <form action="/hapus_polling/{{ item.id }}" method="POST" style="display:inline;">
                                <button class="btn btn-sm btn-danger" onclick="return confirm('Hapus permanen?')">X</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="3" class="text-center text-muted py-3">Belum ada pertanyaan</td></tr>
                {% endif %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    {% if halaman == 'token' %}
    <div class="card shadow border-primary mx-auto" style="max-width: 600px;">
        <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Token Tersedia (ID: {{ id_poll }})</h5>
        </div>
        <div class="card-body">
            <p>Copy link ini untuk pemilih:</p>
            <ul class="list-group mb-3">
            {% for link in daftar_link %}
                <li class="list-group-item bg-light"><a href="{{ link }}" target="_blank" class="text-decoration-none">{{ link }}</a></li>
            {% endfor %}
            </ul>
            <a href="/dashboard" class="btn btn-outline-dark w-100">Kembali</a>
        </div>
    </div>
    {% endif %}

    {% if halaman == 'coblos' %}
    <div class="card shadow border-success mx-auto" style="max-width: 500px;">
        <div class="card-header bg-success text-white text-center">Formulir Pemilihan</div>
        <div class="card-body text-center p-4">
            <h3 class="mb-3">{{ soal }}</h3>
            <span class="badge bg-secondary mb-4">Kode Token: {{ token_user }}</span>
            <form action="/kirim_suara" method="POST">
                <input type="hidden" name="token" value="{{ token_user }}">
                <input type="hidden" name="id_poll" value="{{ id_poll }}">
                <div class="d-grid gap-2">
                {% for i in range(opsi|length) %}
                    <button name="pilihan" value="{{ i }}" class="btn btn-outline-success btn-lg">{{ opsi[i] }}</button>
                {% endfor %}
                </div>
            </form>
        </div>
    </div>
    {% endif %}

    {% if halaman == 'grafik' %}
    <div class="card shadow border-warning mx-auto" style="max-width: 600px;">
        <div class="card-header bg-warning text-center fw-bold">Hasil Perhitungan</div>
        <div class="card-body">
            {% if data_hasil %}
                <h4 class="text-center mb-4">{{ data_hasil.soal }}</h4>
                <ul class="list-group">
                {% for nama, jumlah in data_hasil.hasil.items() %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        {{ nama }} <span class="badge bg-primary rounded-pill">{{ jumlah }} Suara</span>
                    </li>
                {% endfor %}
                </ul>
            {% else %}
                <p class="text-center">Data masih kosong.</p>
            {% endif %}
            <div class="text-center mt-4">
                <a href="/lihat_grafik/{{ id_poll }}" class="btn btn-secondary me-2">Refresh</a>
                {% if session.get('admin_user') %} <a href="/dashboard" class="btn btn-outline-dark">Kembali</a> {% endif %}
            </div>
        </div>
    </div>
    {% endif %}

    {% if halaman == 'pesan' %}
    <div class="text-center mt-5">
        <h1 class="display-1">{{ ikon }}</h1>
        <h3>{{ judul }}</h3>
        <p class="lead text-muted">{{ detail }}</p>
        <br>
        {% if session.get('admin_user') %}
            <a href="/dashboard" class="btn btn-primary">Kembali ke Admin</a>
        {% else %}
            <a href="/" class="btn btn-outline-primary">Halaman Utama</a>
        {% endif %}
    </div>
    {% endif %}

  </div>
</body>
</html>
"""

# routing website

@app.route('/')
def index():
    # jika sudah login lempar ke dashboard
    if 'admin_user' in session: return redirect('/dashboard')
    return render_template_string(TAMPILAN_HTML, halaman='login')

@app.route('/proses_login', methods=['POST'])
def aksi_login():
    try:
        # mengirim data ke node auth port 5001
        data_login = {
            'username': request.form['user'],
            'password': request.form['pass']
        }
        res = requests.post(f'{SERVER_AUTH}/login', json=data_login)
        
        if res.status_code == 200:
            session['admin_user'] = request.form['user']
            return redirect('/dashboard')
        
        return render_template_string(TAMPILAN_HTML, halaman='login', notif="Username/Password Salah!", warna="alert-danger")
    except:
        return render_template_string(TAMPILAN_HTML, halaman='login', notif="Gagal konek ke Server Auth", warna="alert-danger")

@app.route('/logout')
def logout():
    session.pop('admin_user', None)
    return redirect('/')

@app.route('/dashboard')
def menu_admin():
    if 'admin_user' not in session: return redirect('/')
    
    list_polling = []
    try:
        # mengambil data dari node result port 5004
        r = requests.get(f'{SERVER_DATA}/history')
        if r.status_code == 200:
            list_polling = r.json().get('daftar_polling', [])
    except:
        print("cek node 3")

    return render_template_string(TAMPILAN_HTML, halaman='admin', data_history=list_polling, session=session)

# fitur delete
@app.route('/hapus_polling/<id_nya>', methods=['POST'])
def aksi_hapus(id_nya):
    if 'admin_user' not in session: return redirect('/')
    try:
        res = requests.post(f'{SERVER_DATA}/delete/{id_nya}')
        print(f"Status Hapus ID {id_nya}: {res.status_code}")
    except Exception as e:
        print(f"Error saat menghapus: {e}")
        
    return redirect('/dashboard')

@app.route('/buat_baru', methods=['POST'])
def aksi_buat():
    if 'admin_user' not in session: return redirect('/')
    try:
        # mengirim pertanyaan ke node poll port 5002
        paket_soal = {
            "question": request.form['pertanyaan'], 
            "options": [request.form['opsi_a'], request.form['opsi_b']]
        }
        # menggunakan requests.post untuk RPC
        res_poll = requests.post(f'{SERVER_SOAL}/create', json=paket_soal)
        
        if res_poll.status_code != 201:
             return render_template_string(TAMPILAN_HTML, halaman='admin', session=session, notif=f"Gagal: {res_poll.text}", warna="alert-danger")

        # meminta node token port 5005 membuat token
        id_baru = res_poll.json()['poll_id']
        requests.post(f'{SERVER_TOKEN}/generate_tokens', json={
            'poll_id': id_baru, 'count': request.form['jumlah']
        })
        
        return redirect('/dashboard')
        
    except Exception as e:
        return render_template_string(TAMPILAN_HTML, halaman='admin', session=session, notif=f"Error sistem: {str(e)}", warna="alert-danger")

@app.route('/lihat_token/<id_nya>')
def halaman_token(id_nya):
    if 'admin_user' not in session: return redirect('/')
    try:
        r = requests.get(f'{SERVER_DATA}/tokens/{id_nya}')
        link_ada = r.json().get('link_tersedia', [])
        return render_template_string(TAMPILAN_HTML, halaman='token', daftar_link=link_ada, id_poll=id_nya)
    except: return "Gagal ambil token dari database"

@app.route('/vote/<id_nya>')
def halaman_vote(id_nya):
    token_dari_url = request.args.get('t')
    try:
        # ambil detail pertanyaan buat ditampilin
        r = requests.get(f'{SERVER_DATA}/summary/{id_nya}').json()
        if 'soal' not in r: return "Polling tidak ditemukan atau sudah dihapus"
        
        # Kirim data ke HTML
        return render_template_string(TAMPILAN_HTML, halaman='coblos', 
                                      soal=r['soal'], 
                                      opsi=list(r['hasil'].keys()), 
                                      token_user=token_dari_url, 
                                      id_poll=id_nya)
    except: return "gagal connect ke server data"

@app.route('/kirim_suara', methods=['POST'])
def aksi_kirim_suara():
    try:
        # prepare data buat dikirim ke node vote
        data_suara = {
            'token': request.form['token'],
            'poll_id': request.form['id_poll'],
            'choice': int(request.form['pilihan']) # dijadikan integer
        }
        
        # send to node vote port 5003
        r = requests.post(f'{SERVER_VOTE}/submit', json=data_suara)
        
        if r.status_code == 200:
            return render_template_string(TAMPILAN_HTML, halaman='pesan', judul="Terima Kasih", detail="Suara anda sudah masuk")
        
        # if gagal
        pesan_error = r.json().get('msg', 'Error tidak diketahui')
        return render_template_string(TAMPILAN_HTML, halaman='pesan', judul="GAGAL", detail=pesan_error)
        
    except Exception as e:
        return f"Error di Frontend: {e}"

@app.route('/lihat_grafik/<id_nya>')
def halaman_grafik(id_nya):
    try:
        r = requests.get(f'{SERVER_DATA}/summary/{id_nya}').json()
        return render_template_string(TAMPILAN_HTML, halaman='grafik', data_hasil=r, id_poll=id_nya, session=session)
    except: return render_template_string(TAMPILAN_HTML, halaman='admin', session=session, notif="Node 3 ga respon", warna="alert-danger")

if __name__ == '__main__':
    print("FRONTEND PORT 5000")
    app.run(port=5000)