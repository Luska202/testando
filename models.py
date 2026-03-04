import sqlite3
import hashlib
import json
import os

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def init_db():
    with get_db() as db:
        # Tabelas
        db.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                nome TEXT NOT NULL,
                data_nascimento DATE,
                admin INTEGER DEFAULT 0,
                favoritos TEXT DEFAULT '[]',
                banned INTEGER DEFAULT 0
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS filmes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                sinopse TEXT,
                categoria TEXT,
                logo_url TEXT,
                video_path TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                sinopse TEXT,
                categoria TEXT,
                logo_url TEXT,
                temporada INTEGER,
                episodio INTEGER,
                video_path TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(titulo, temporada, episodio)
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS progresso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                conteudo_id INTEGER,
                tipo TEXT,
                temporada INTEGER,
                episodio INTEGER,
                tempo_assistido INTEGER DEFAULT 0,
                duracao_total INTEGER,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
        ''')
        db.commit()

        # Criar usuário administrador padrão se não existir
        criar_admin_padrao(db)

def criar_admin_padrao(db):
    # Verifica se já existe algum admin
    admin = db.execute('SELECT * FROM usuarios WHERE admin = 1 LIMIT 1').fetchone()
    if not admin:
        # Cria um admin padrão
        email = 'admin@example.com'
        senha = 'admin123'  # Em produção, use variável de ambiente
        nome = 'Administrador'
        senha_hash = hash_senha(senha)
        try:
            db.execute('''
                INSERT INTO usuarios (email, senha, nome, admin)
                VALUES (?, ?, ?, ?)
            ''', (email, senha_hash, nome, 1))
            db.commit()
            print("Usuário administrador padrão criado:")
            print(f"E-mail: {email}")
            print(f"Senha: {senha}")
            print("Altere essas credenciais após o primeiro login.")
        except sqlite3.IntegrityError:
            # Se o email já existir (improvável), não faz nada
            pass

# Funções auxiliares (já existiam)
def get_favoritos(usuario_id):
    db = get_db()
    row = db.execute('SELECT favoritos FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()
    if row and row['favoritos']:
        return json.loads(row['favoritos'])
    return []

def add_favorito(usuario_id, item_id, tipo):
    favs = get_favoritos(usuario_id)
    novo = {'id': item_id, 'tipo': tipo}
    if novo not in favs:
        favs.append(novo)
        db = get_db()
        db.execute('UPDATE usuarios SET favoritos = ? WHERE id = ?', (json.dumps(favs), usuario_id))
        db.commit()

def remove_favorito(usuario_id, item_id, tipo):
    favs = get_favoritos(usuario_id)
    favs = [f for f in favs if not (f['id'] == item_id and f['tipo'] == tipo)]
    db = get_db()
    db.execute('UPDATE usuarios SET favoritos = ? WHERE id = ?', (json.dumps(favs), usuario_id))
    db.commit()