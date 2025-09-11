from flask import Flask, render_template, request, redirect, url_for, session
#from flask_login import login_required
from verifiers import isUsernameValid, isPasswordValid
import os, sqlite3, json, requests

class RemoteSQLite:
    def __init__(self, db_api_url):
        self.api_url = db_api_url
    
    def execute_query(self, query, params=None):
        if params is None:
            params = []
            
        payload = {
            'query': query,
            'params': params
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/query",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Connection error: {str(e)}'}

app = Flask(__name__)
app.secret_key = "plantractor"


BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DB_API_URL = "http://10.0.1.30:5001"
db = RemoteSQLite(DB_API_URL)

def init_db():
    result = db.execute_query("CREATE TABLE IF NOT EXISTS users (id_user INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    if result['success']:
        return 
    
    raise RuntimeError("Não foi possivel se iniciar o banco de dados")

@app.route('/', methods=['GET', 'POST'])
def home():
    #logged_in = 'username' in session
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_username = None
    error_password = None
    error_user = None
    error = None
    success_message = None

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if request.method == 'POST':
        if not isUsernameValid(username):
            error_username = 'Usuário inválido!'
        elif not isPasswordValid(password):
            error_password = 'Senha inválida!'
        else:
            user_response = db.execute_query("SELECT * FROM users WHERE username=?", [username])

            if user_response['success'] and user_response.get('data'):  # já existe
                error_user = 'Usuário já existe!'
            else:
                insert_response = db.execute_query("INSERT INTO users (username, password) VALUES (?, ?)", [username, password])

                if insert_response['success']:
                    success_message = 'Conta criada com sucesso!'
                else:
                    error = 'Erro interno do servidor !'

    return render_template('register.html', error_username=error_username, error_password=error_password, error_user=error_user, error=error, success_message=success_message, username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_username = None
    error_password = None
    error = None

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if request.method == 'POST':
        user_response = db.execute_query("SELECT id_user, username, password FROM users WHERE username=?", [username])

        if user_response['success'] and user_response.get('data'):
            user_data = user_response['data'][0] if isinstance(user_response['data'], list) else user_response['data']
            db_username = user_data['username']
            db_password = user_data['password']

            if password == db_password:
                session['username'] = db_username
                return redirect(url_for('profile'))
            else:
                error_password = 'Senha incorreta!'
        else:
            error_username = 'Usuário não encontrado'

    return render_template('login.html', error_username=error_username, error_password=error_password, error=error, username=username)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    user_response = db.execute_query("SELECT * FROM users WHERE username=?", [username])
    
    if user_response['success'] and user_response.get('data'):
        return render_template('perfil.html', username=username)
    else:
        return "Erro interno do servidor!", 500

@app.route("/plantas")
def minhas_plantas():
    json_path = os.path.join(app.root_path, "plantas.json")

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            plantas = json.load(f)
    else:
        plantas = []

    return render_template("plantas.html", plantas=plantas)

@app.route('/rotina')
def rotina():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    plants_json = os.path.join(BASE_DIR, 'plantas.json')

    with open(plants_json, 'r', encoding='utf-8') as file:
        plantas = json.load(file)

    return render_template('rotina.html', plantas=plantas, username=username)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)