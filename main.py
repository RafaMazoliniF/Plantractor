from flask import Flask, render_template, request, redirect, url_for, session
#from flask_login import login_required
from verifiers import isUsernameValid, isPasswordValid
import os, sqlite3, json

app = Flask(__name__)
app.secret_key = "plantractor"

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DB_PATH = os.path.join(BASE_DIR, 'database.db') 

def init_db():
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id_user INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    con.commit()
    con.close()

def execute_query(query, params=None, fetchone=True):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    c = con.cursor()
    
    if params:
        c.execute(query, params)
    else:
        c.execute(query)
    
    if query.strip().upper().startswith('SELECT'):
        response = c.fetchone() if fetchone else c.fetchall()
    else:
        con.commit()
        response = c.rowcount
    
    con.close()
    return response

@app.route('/', methods=['GET', 'POST'])
def home():
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
            user_response = execute_query("SELECT * FROM users WHERE username=?", (username,))

            if user_response:  # já existe
                error_user = 'Usuário já existe!'
            else:
                rows_updated = execute_query("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

                if rows_updated > 0:
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

    print(username, password)
    if request.method == 'POST':
        user_response = execute_query("SELECT id_user, username, password FROM users WHERE username=?", (username,))

        if user_response:
            #user = user_response[0] #primeira coisa
            db_username = user_response['username']
            db_password = user_response['password']

            if password == db_password:
                session['username'] = db_username
                return redirect(url_for('profile'))
            else:
                error_password = 'Senha incorreta!'
        else:
            error_username = 'Usuário não encontrado'

    print(error_password, error_username)
    return render_template('login.html', error_username=error_username, error_password=error_password, error=error, username=username)

@app.route('/profile')
def profile():
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()

    error = None

    username = session['username']
    plants_json = os.path.join(BASE_DIR, 'plantas.json') 

    with open(plants_json, 'r', encoding='utf-8') as file:
        plantas = json.load(file)

    user_response = execute_query("SELECT * FROM users WHERE username=?", (username,))
    
    if user_response:
        return render_template('plantas.html', plantas=plantas)
    else:
        error = 'Erro interno do servidor!'

@app.route('/rotine')
def rotine():
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()

    error = None

    username = session['username']
    plants_json = os.path.join(BASE_DIR, 'plantas.json') 

    with open(plants_json, 'r', encoding='utf-8') as file:
        plantas = json.load(file)

    user_response = execute_query("SELECT * FROM users WHERE username=?", (username,))
    
    if user_response:
        return render_template('rotina.html')
    else:
        error = 'Erro interno do servidor!'

@app.route('/logout')
def logout():
    return render_template('login.html')

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
