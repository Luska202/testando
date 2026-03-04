from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import get_db, init_db
from auth import *
from admin import *
from player import *
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_muito_segura'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Inicializa o banco na primeira execução
with app.app_context():
    init_db()

# Rotas de autenticação
@app.route('/')
def home():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = verificar_login(email, senha)
        if usuario:
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            session['usuario_admin'] = usuario['admin']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', erro='Credenciais inválidas')
    return render_template('login.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        if registrar_usuario(nome, email, senha):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', erro='E-mail já existe')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Rotas principais (protegidas)
@app.route('/index')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    # Buscar últimos cadastrados e últimos assistidos
    return render_template('index.html')

# ... demais rotas (filmes, series, admin, perfil, etc.)