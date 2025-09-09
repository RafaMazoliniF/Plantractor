from flask import Flask, render_template, request
from verifiers import isEmailValid, isPasswordValid
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()

    error_email, error_password, error_not_user, error= None, None, None, None

    email = request.form['email']
    password = request.form['password']

    if isEmailValid(email):
        if isPasswordValid(password):
            c.execute("SELECT email, password FROM users WHERE email=?", (email,))
            user_response = c.fetchone()

            if user_response:
                if user_response['email'] == email and user_response['password'] == password:
                    #fazerlogin
                    pass
                else:
                    error_not_user = 'Usuário não existe!'
            else:
                error = 'Erro interno no servidor!'
        else:
            error_password = 'Senha inválida!'
    else:
        error_email = 'Email inválido!'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
