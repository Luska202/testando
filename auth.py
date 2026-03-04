from models import get_db, hash_senha

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