from flask import Flask, render_template_string, request, redirect, session, url_for
import requests

app = Flask(__name__)
app.secret_key = 'rahasia' 

# alamat API
API_USER = 'http://localhost:5001'
API_POLL = 'http://localhost:5002'
API_VOTE = 'http://localhost:5003'
API_RESULT = 'http://localhost:5004'
API_SHARE = 'http://localhost:5005'

# web interface
TAMPILAN_WEB = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <title>Sistem E-Voting</title>
  <style>body { background-color: #f8f9fa; padding-top: 2rem; }</style>
</head>
<body>
  <div class="container" style="max-width: 850px;">
    
    {% if msg %}
    <div class="alert {{ color }} alert-dismissible fade show">
        {{ msg }} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    {% endif %}

    {% if page == 'login' %}
    <div class="card shadow p-4 mx-auto" style="max-width: 400px;">
        <h3 class="text-center mb-3">Login Admin</h3>
        <form action="/auth/login" method="POST">
            <input name="username" class="form-control mb-2" value="admin" placeholder="Username">
            <input type="password" name="password" class="form-control mb-2" value="rahasia" placeholder="Password">
            <button class="btn btn-primary w-100">Masuk</button>
        </form>
    </div>
    {% endif %}

    {% if page == 'admin' %}
    <div class="card shadow mb-4">
        <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <span>Dashboard Admin</span>
            <a href="/logout" class="text-white">Logout</a>
        </div>
        <div class="card-body">
            <form action="/admin/create" method="POST">
                <input class="form-control mb-2" name="q" placeholder="Mau tanya apa?" required>
                <div class="row g-2 mb-2">
                    <div class="col"><input class="form-control" name="opt1" placeholder="Pilihan A" required></div>
                    <div class="col"><input class="form-control" name="opt2" placeholder="Pilihan B" required></div>
                </div>
                <input type="number" class="form-control mb-3" name="count" value="3" placeholder="Jumlah Token">
                <button class="btn btn-primary w-100">Buat Polling</button>
            </form>
        </div>
    </div>

    <div class="card shadow">
        <div class="card-header bg-secondary text-white">Riwayat Polling</div>
        <div class="card-body p-0">
            <table class="table table-striped mb-0">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Pertanyaan</th>
                        <th class="text-end">Aksi</th>
                    </tr>
                </thead>
                <tbody>
                {% if history %}
                    {% for item in history %}
                    <tr>
                        <td>#{{ item.id }}</td>
                        <td>{{ item.question }}</td>
                        <td class="text-end">
                            <a href="/show_tokens/{{ item.id }}" class="btn btn-sm btn-success">Ambil Token</a>
                            <a href="/result_view/{{ item.id }}" class="btn btn-sm btn-warning">Lihat Hasil</a>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="3" class="text-center text-muted">Belum ada data polling.</td></tr>
                {% endif %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    {% if page == 'tokens' %}
    <div class="card shadow border-success mx-auto" style="max-width: 600px;">
        <div class="card-header bg-success text-white">
            <h5 class="mb-0">Daftar Token (Poll #{{ pid }})</h5>
        </div>
        <div class="card-body">
            <p>Copy link di bawah ini buat pemilih:</p>
            <ul class="list-group mb-3">
            {% for link in links %}
                <li class="list-group-item"><a href="{{ link }}" target="_blank">{{ link }}</a></li>
            {% endfor %}
            </ul>
            <a href="/admin" class="btn btn-outline-dark w-100">Kembali</a>
        </div>
    </div>
    {% endif %}

    {% if page == 'vote' %}
    <div class="card shadow border-primary mx-auto" style="max-width: 500px;">
        <div class="card-header bg-success text-white text-center">Harap dijawab dengan serius</div>
        <div class="card-body text-center">
            <h4>{{ soal }}</h4>
            <span class="badge bg-secondary mb-4">Tiket: {{ token }}</span>
            <form action="/submit_vote" method="POST">
                <input type="hidden" name="token" value="{{ token }}">
                <input type="hidden" name="pid" value="{{ pid }}">
                {% for i in range(opsi|length) %}
                <button name="choice" value="{{ i }}" class="btn btn-outline-success btn-lg w-100 mb-2">{{ opsi[i] }}</button>
                {% endfor %}
            </form>
        </div>
    </div>
    {% endif %}

    {% if page == 'result' %}
    <div class="card shadow border-warning mx-auto" style="max-width: 600px;">
        <div class="card-header bg-warning text-center fw-bold">Hasil Sementara (Poll #{{ pid }})</div>
        <div class="card-body">
            {% if data %}
                <h4 class="text-center mb-4">{{ data.soal }}</h4>
                <ul class="list-group">
                {% for k,v in data.hasil.items() %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        {{ k }} <span class="badge bg-primary rounded-pill fs-6">{{ v }} Suara</span>
                    </li>
                {% endfor %}
                </ul>
            {% else %}
                <p class="text-center text-muted">Datanya kosong.</p>
            {% endif %}
            <div class="text-center mt-3 gap-2">
                <a href="/result_view/{{ pid }}" class="btn btn-secondary">Refresh Data</a>
                {% if session.get('user') %} <a href="/admin" class="btn btn-outline-dark">Kembali ke Admin</a> {% endif %}
            </div>
        </div>
    </div>
    {% endif %}

    {% if page == 'msg' %}
    <div class="text-center mt-5">
        <h1>{{ icon }}</h1>
        <h3>{{ title }}</h3>
        <p class="text-muted">{{ detail }}</p>
        <br>
    </div>
    {% endif %}

  </div>
</body>
</html>
"""

@app.route('/')
def halaman_utama():
    if 'user' in session: return redirect('/admin')
    return render_template_string(TAMPILAN_WEB, page='login')

@app.route('/auth/login', methods=['POST'])
def proses_login():
    try:
        # mengirim data login ke node user
        res = requests.post(f'{API_USER}/login', json=request.form)
        
        if res.status_code == 200:
            session['user'] = request.form['username']
            return redirect('/admin')
        return render_template_string(TAMPILAN_WEB, page='login', msg="Password salah bro", color="alert-danger")
    except:
        return render_template_string(TAMPILAN_WEB, page='login', msg="Server Auth mati", color="alert-danger")

@app.route('/logout')
def keluar():
    session.pop('user', None)
    return redirect('/')

@app.route('/admin')
def dashboard_admin():
    if 'user' not in session: return redirect('/')
    
    # mengambil riwayat polling dari database
    list_history = []
    try:
        r = requests.get(f'{API_RESULT}/history')
        if r.status_code == 200:
            list_history = r.json().get('polls', [])
    except:
        pass # biarin kosong kalau error

    return render_template_string(TAMPILAN_WEB, page='admin', history=list_history, session=session)

@app.route('/admin/create', methods=['POST'])
def buat_polling():
    if 'user' not in session: return redirect('/')
    try:
        # 1. kirim pollinng ke api poll
        data_soal = {
            "question": request.form['q'], 
            "options": [request.form['opt1'], request.form['opt2']]
        }
        r_poll = requests.post(f'{API_POLL}/create', json=data_soal)
        
        if r_poll.status_code != 201:
             return render_template_string(TAMPILAN_WEB, page='admin', session=session, msg=f"Gagal membuat poll: {r_poll.text}", color="alert-danger")

        # 2. minta generate token
        id_poll = r_poll.json()['poll_id']
        requests.post(f'{API_SHARE}/generate_tokens', json={
            'poll_id': id_poll, 'count': request.form['count']
        })
        
        return redirect('/admin')
        
    except Exception as e:
        return render_template_string(TAMPILAN_WEB, page='admin', session=session, msg=f"Error sistem: {str(e)}", color="alert-danger")

@app.route('/show_tokens/<pid>')
def lihat_token(pid):
    if 'user' not in session: return redirect('/')
    try:
        r = requests.get(f'{API_RESULT}/tokens/{pid}')
        daftar_link = r.json().get('links', [])
        return render_template_string(TAMPILAN_WEB, page='tokens', links=daftar_link, pid=pid)
    except: return "gagal ambil token"

@app.route('/vote/<pid>')
def halaman_vote(pid):
    kode_token = request.args.get('t')
    try:
        # ambil data soal dari node result
        r = requests.get(f'{API_RESULT}/summary/{pid}').json()
        if 'soal' not in r: return "Polling not found"
        return render_template_string(TAMPILAN_WEB, page='vote', soal=r['soal'], opsi=list(r['hasil'].keys()), token=kode_token, pid=pid)
    except: return "gagal connect ke database"

@app.route('/submit_vote', methods=['POST'])
def kirim_suara():
    try:
        # mengubah data form ke dict
        data_kirim = request.form.to_dict()
        
        # fix bug beda nama variabel pid vs poll_id
        if 'pid' in data_kirim:
            data_kirim['poll_id'] = data_kirim.pop('pid')
        
        # mengirim ke node vote
        r = requests.post(f'{API_VOTE}/submit', json=data_kirim)
        
        if r.status_code == 200:
            return render_template_string(TAMPILAN_WEB, page='msg', title="Terima Kasih", detail="Voting anda sudah diterima")
        
        # meanmpilkan pesan error dari backend
        pesan_error = r.json().get('msg', 'error tidak diketahui')
        return render_template_string(TAMPILAN_WEB, page='msg', title="GAGAL", detail=pesan_error)
        
    except Exception as e:
        return f"Error Frontend: {e}"

@app.route('/result_view/<pid>')
def lihat_hasil(pid):
    try:
        r = requests.get(f'{API_RESULT}/summary/{pid}').json()
        return render_template_string(TAMPILAN_WEB, page='result', data=r, pid=pid, session=session)
    except: return render_template_string(TAMPILAN_WEB, page='admin', session=session, msg="Node 3 ga respon", color="alert-danger")

if __name__ == '__main__':
    print("NODE 2 FRONTEND")
    app.run(port=5000)