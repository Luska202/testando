from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import init_db, get_db, add_favorito, remove_favorito, get_favoritos, hash_senha
from auth import login_required, admin_required, verificar_login, registrar_usuario
from player import salvar_progresso, obter_progresso
import admin
import os

app = Flask(__name__)
app.secret_key = 'chave-super-secreta-para-sessao'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

with app.app_context():
    init_db()

admin.init_admin_routes(app)

def row_to_dict(row):
    return {k: row[k] for k in row.keys()}

# Rotas públicas
@app.route('/')
def home():
    if 'usuario_id' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

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
            return render_template('login.html', erro='E-mail ou senha inválidos')
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
            return render_template('register.html', erro='E-mail já cadastrado')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Rotas protegidas
@app.route('/index')
@login_required
def index():
    db = get_db()
    ultimos_filmes = db.execute('SELECT * FROM filmes ORDER BY data_cadastro DESC LIMIT 5').fetchall()
    ultimos_series = db.execute('SELECT * FROM series ORDER BY data_cadastro DESC LIMIT 5').fetchall()
    
    assistidos = db.execute('''
        SELECT DISTINCT conteudo_id, tipo FROM progresso
        WHERE usuario_id = ?
        ORDER BY id DESC LIMIT 10
    ''', (session['usuario_id'],)).fetchall()
    
    ultimos_assistidos = []
    for a in assistidos:
        if a['tipo'] == 'filme':
            item = db.execute('SELECT id, titulo, logo_url, "filme" as tipo FROM filmes WHERE id = ?', (a['conteudo_id'],)).fetchone()
        else:
            item = db.execute('SELECT id, titulo, logo_url, "serie" as tipo FROM series WHERE id = ?', (a['conteudo_id'],)).fetchone()
        if item:
            ultimos_assistidos.append(item)
    
    return render_template('index.html',
                           ultimos_filmes=ultimos_filmes,
                           ultimos_series=ultimos_series,
                           ultimos_assistidos=ultimos_assistidos)

@app.route('/filmes')
@login_required
def filmes():
    return render_template('filmes.html')

@app.route('/api/filmes')
@login_required
def api_filmes():
    db = get_db()
    search = request.args.get('search', '')
    categoria = request.args.get('categoria', '')
    order = request.args.get('order', 'titulo ASC')
    query = 'SELECT * FROM filmes WHERE 1=1'
    params = []
    if search:
        query += ' AND titulo LIKE ?'
        params.append(f'%{search}%')
    if categoria:
        query += ' AND categoria = ?'
        params.append(categoria)
    query += f' ORDER BY {order}'
    filmes = db.execute(query, params).fetchall()
    return jsonify([row_to_dict(f) for f in filmes])

@app.route('/series')
@login_required
def series():
    return render_template('series.html')

@app.route('/api/series')
@login_required
def api_series():
    db = get_db()
    search = request.args.get('search', '')
    categoria = request.args.get('categoria', '')
    order = request.args.get('order', 'titulo ASC')
    query = 'SELECT * FROM series WHERE 1=1'
    params = []
    if search:
        query += ' AND titulo LIKE ?'
        params.append(f'%{search}%')
    if categoria:
        query += ' AND categoria = ?'
        params.append(categoria)
    query += f' ORDER BY {order}'
    series = db.execute(query, params).fetchall()
    return jsonify([row_to_dict(s) for s in series])

@app.route('/filme/<int:id>')
@login_required
def filme_detalhe(id):
    db = get_db()
    filme = db.execute('SELECT * FROM filmes WHERE id = ?', (id,)).fetchone()
    if not filme:
        return redirect(url_for('filmes'))
    return render_template('filme.html', filme=filme)

@app.route('/serie/<int:id>')
@login_required
def serie_detalhe(id):
    db = get_db()
    serie = db.execute('SELECT * FROM series WHERE id = ?', (id,)).fetchone()
    if not serie:
        return redirect(url_for('series'))
    episodios = db.execute('''
        SELECT * FROM series WHERE titulo = ? ORDER BY temporada, episodio
    ''', (serie['titulo'],)).fetchall()
    return render_template('serie.html', serie=serie, episodios=episodios)

@app.route('/favoritos')
@login_required
def favoritos():
    favs = get_favoritos(session['usuario_id'])
    itens = []
    db = get_db()
    for fav in favs:
        if fav['tipo'] == 'filme':
            item = db.execute('SELECT id, titulo, logo_url, "filme" as tipo FROM filmes WHERE id = ?', (fav['id'],)).fetchone()
        else:
            item = db.execute('SELECT id, titulo, logo_url, "serie" as tipo FROM series WHERE id = ?', (fav['id'],)).fetchone()
        if item:
            itens.append(item)
    return render_template('favoritos.html', itens=itens)

@app.route('/favoritar', methods=['POST'])
@login_required
def favoritar():
    data = request.get_json()
    acao = data.get('acao')
    item_id = data.get('id')
    tipo = data.get('tipo')
    if acao == 'add':
        add_favorito(session['usuario_id'], item_id, tipo)
    else:
        remove_favorito(session['usuario_id'], item_id, tipo)
    return '', 204

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    db = get_db()
    usuario = db.execute('SELECT * FROM usuarios WHERE id = ?', (session['usuario_id'],)).fetchone()
    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        if usuario['senha'] != hash_senha(senha_atual):
            return render_template('perfil.html', usuario=usuario, erro='Senha atual incorreta')
        novo_nome = request.form.get('nome', usuario['nome'])
        novo_email = request.form.get('email', usuario['email'])
        nova_data = request.form.get('data_nascimento') or None
        nova_senha = request.form.get('nova_senha')
        if nova_senha:
            nova_senha_hash = hash_senha(nova_senha)
        else:
            nova_senha_hash = usuario['senha']
        db.execute('''
            UPDATE usuarios SET nome=?, email=?, data_nascimento=?, senha=?
            WHERE id=?
        ''', (novo_nome, novo_email, nova_data, nova_senha_hash, session['usuario_id']))
        db.commit()
        session['usuario_nome'] = novo_nome
        return redirect(url_for('perfil'))
    return render_template('perfil.html', usuario=usuario)

# Player
@app.route('/player/filme/<int:id>')
@login_required
def player_filme(id):
    db = get_db()
    filme = db.execute('SELECT * FROM filmes WHERE id = ?', (id,)).fetchone()
    if not filme:
        return redirect(url_for('filmes'))
    return render_template('player_page.html', id=id, tipo='filme', temporada=None, episodio=None, video_path=filme['video_path'])

@app.route('/player/serie/<int:id>')
@login_required
def player_serie(id):
    temporada = request.args.get('temporada', type=int)
    episodio = request.args.get('episodio', type=int)
    db = get_db()
    serie = db.execute('SELECT * FROM series WHERE id = ?', (id,)).fetchone()
    if not serie:
        return redirect(url_for('series'))
    return render_template('player_page.html', id=id, tipo='serie', temporada=temporada, episodio=episodio, video_path=serie['video_path'])

# API de progresso
@app.route('/api/progresso')
@login_required
def api_progresso():
    tipo = request.args.get('tipo')
    conteudo_id = request.args.get('id')
    temporada = request.args.get('temporada', type=int)
    episodio = request.args.get('episodio', type=int)
    tempo = obter_progresso(session['usuario_id'], conteudo_id, tipo, temporada, episodio)
    return jsonify({'tempo': tempo})

@app.route('/api/salvar_progresso', methods=['POST'])
@login_required
def api_salvar_progresso():
    data = request.get_json()
    salvar_progresso(
        session['usuario_id'],
        data['id'],
        data['tipo'],
        data.get('temporada'),
        data.get('episodio'),
        data['tempo_assistido'],
        data.get('duracao_total')
    )
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)