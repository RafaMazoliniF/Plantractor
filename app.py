from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Necessário para flash messages

# Página inicial
@app.route("/")
def home():
    return render_template("index.html")

# Página de plantas
@app.route("/plantas")
def minhas_plantas():
    json_path = os.path.join(app.root_path, "plantas.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            plantas = json.load(f)
    else:
        plantas = []
    return render_template("plantas.html", plantas=plantas)

# Página de rotina
@app.route("/rotina")
def rotina():
    json_path = os.path.join(app.root_path, "rotina.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            tarefas = json.load(f)
    else:
        tarefas = []
    return render_template("rotina.html", tarefas=tarefas)

# Página de registro
@app.route('/register', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        users_path = os.path.join(app.root_path, "users.json")
        if os.path.exists(users_path):
            with open(users_path, "r", encoding="utf-8") as f:
                users = json.load(f)
        else:
            users = []

        # Verifica se o usuário já existe
        if any(u["usuario"] == usuario for u in users):
            flash("Usuário já existe!", "error")
            return redirect(url_for('registro'))

        users.append({"usuario": usuario, "senha": senha})

        with open(users_path, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)

        flash("Registro realizado com sucesso! Faça login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        users_path = os.path.join(app.root_path, "users.json")
        if os.path.exists(users_path):
            with open(users_path, "r", encoding="utf-8") as f:
                users = json.load(f)
        else:
            users = []

        # Verifica se o usuário e senha existem
        user = next((u for u in users if u["usuario"] == usuario and u["senha"] == senha), None)
        if user:
            flash(f"Bem-vindo, {usuario}!", "success")
            return redirect(url_for('home'))
        else:
            flash("Usuário ou senha incorretos.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
