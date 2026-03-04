from flask import session, redirect, url_for
from models import get_db, hash_senha
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or session.get('usuario_admin') != 1:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def verificar_login(email, senha):
    db = get_db()
    usuario = db.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
    if usuario and usuario['senha'] == hash_senha(senha) and not usuario['banned']:
        return usuario
    return None

def registrar_usuario(nome, email, senha):
    db = get_db()
    try:
        db.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
                   (nome, email, hash_senha(senha)))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False