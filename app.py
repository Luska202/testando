from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
app.secret_key = "super_secret_key"
bcrypt = Bcrypt(app)

# Criar banco automaticamente
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            sobrenome TEXT,
            email TEXT UNIQUE,
            senha TEXT,
            nascimento TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/home")
def home():
    if "user" in session:
        return render_template("home.html")
    return redirect(url_for("login_page"))

@app.route("/register_user", methods=["POST"])
def register_user():
    nome = request.form["nome"]
    sobrenome = request.form["sobrenome"]
    email = request.form["email"]
    senha = request.form["senha"]
    nascimento = request.form["nascimento"]

    senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (nome, sobrenome, email, senha, nascimento)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, sobrenome, email, senha_hash, nascimento))
        conn.commit()
        conn.close()
        return redirect(url_for("login_page"))
    except:
        return "Email já cadastrado!"

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    senha = request.form["senha"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[0], senha):
        session["user"] = email
        return redirect(url_for("home"))
    else:
        return "Login inválido!"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login_page"))

if __name__ == "__main__":
    app.run(debug=True)