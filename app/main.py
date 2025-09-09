from flask import Flask, render_template, request, redirect, url_for, session, login_required
from verifiers import isUsernameValid, isPasswordValid
import os, sqlite3

app = Flask(__name__)
app.secret_key = "plantractor"

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DB_PATH = os.path.join(BASE_DIR, 'database.db') 

def init_db():
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id_user INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    con.commit()
    con.close()

def execute_query(query, params=None):
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()
    
    if params:
        c.execute(query, params)
    else:
        c.execute(query)
    
    if query.strip().upper().startswith('SELECT'):
        response = c.fetchone()
    else:
        con.commit()
        response = c.rowcount
    
    con.close()
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()

    error_username, error_password, error_user, error = None, None, None, None

    username = request.form['username']
    password = request.form['password']

    if isUsernameValid(username):
        if isPasswordValid(password):
            user_response = execute_query("SELECT * FROM users WHERE email=?", (username, ))

            if not user_response: #n tem nenhum registro desse user
                rows_updated = execute_query("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                
                if rows_updated > 0:
                    return redirect(url_for('login'))
                else:
                    error = 'Erro interno do servidor!'
            else: #ja tem o user
                error_user = 'Usuário já existe!'
        else:
            error_password = 'Senha inválida!'
    else:
        error_username = 'Usuário inválido!'

    con.close()

    return render_template('register.html', error_username=error_username, error_password=error_password, error_user=error_user, error=error, username=username) 

@app.route('/login', methods=['GET', 'POST'])
def login():
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()

    error_username, error_password, error = None, None, None, None

    username = request.form['username']
    password = request.form['password']

    user_response = execute_query("SELECT id_user, username, password FROM users WHERE email=? ", (username, ))

    if user_response:
        if username == user_response['username']:
            if password == user_response['password']:
                session['username'] = username 
                return redirect(url_for('profile'), id_user=user_response['id_user'])
            else:
                error_password = 'Senha incorreta!'
        else:
            error_username = 'Esse usuário não existe!'
    else:
        error = 'Erro interno do servidor!'

    return render_template('login.html', error_username=error_username, error_password=error_password, error=error, username=username)

@app.route('/profile')
@login_required
def profile():
    username = session['username']
    
    user_response = execute_query("SELECT * FROM users WHERE username=?", (username,))
    
    if user_response:
        return render_template('profile.html')
    else:
        error = 'Erro interno do servidor!'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
