from flask import render_template, request, redirect, url_for, session
from auth import admin_required
from models import get_db, hash_senha
from werkzeug.utils import secure_filename
import os

def init_admin_routes(app):
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        db = get_db()
        total_filmes = db.execute('SELECT COUNT(*) as c FROM filmes').fetchone()['c']
        total_series = db.execute('SELECT COUNT(*) as c FROM series').fetchone()['c']
        total_usuarios = db.execute('SELECT COUNT(*) as c FROM usuarios').fetchone()['c']
        return render_template('admin/dashboard.html', total_filmes=total_filmes, total_series=total_series, total_usuarios=total_usuarios)

    @app.route('/admin/usuarios', methods=['GET', 'POST'])
    @admin_required
    def admin_usuarios():
        db = get_db()
        if request.method == 'POST':
            acao = request.form.get('acao')
            usuario_id = request.form.get('usuario_id')
            if acao == 'toggle_admin':
                db.execute('UPDATE usuarios SET admin = NOT admin WHERE id = ?', (usuario_id,))
            elif acao == 'banir':
                db.execute('UPDATE usuarios SET banned = 1 WHERE id = ?', (usuario_id,))
            elif acao == 'excluir':
                # Remove progresso do usuário antes de excluir
                db.execute('DELETE FROM progresso WHERE usuario_id = ?', (usuario_id,))
                db.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
            elif acao == 'criar':
                email = request.form['email']
                senha = request.form['senha']
                try:
                    db.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
                               ('Usuário', email, hash_senha(senha)))
                except:
                    pass
            db.commit()
        usuarios = db.execute('SELECT id, email, admin, banned FROM usuarios').fetchall()
        return render_template('admin/usuarios.html', usuarios=usuarios)

    @app.route('/admin/cadastro', methods=['GET', 'POST'])
    @admin_required
    def admin_cadastro_conteudo():
        db = get_db()
        if request.method == 'POST':
            tipo = request.form['tipo']
            titulo = request.form['titulo']
            sinopse = request.form['sinopse']
            categoria = request.form['categoria']
            logo_url = request.form['logo_url']
            video = request.files['video']
            if video:
                filename = secure_filename(f"{tipo}_{titulo}_{video.filename}")
                video_path = os.path.join('static/uploads', filename)
                video.save(video_path)
                video_path_db = f"uploads/{filename}"
            else:
                video_path_db = ''
            if tipo == 'filme':
                db.execute('INSERT INTO filmes (titulo, sinopse, categoria, logo_url, video_path) VALUES (?,?,?,?,?)',
                           (titulo, sinopse, categoria, logo_url, video_path_db))
            else:
                temporada = request.form['temporada']
                episodio = request.form['episodio']
                db.execute('INSERT INTO series (titulo, sinopse, categoria, logo_url, temporada, episodio, video_path) VALUES (?,?,?,?,?,?,?)',
                           (titulo, sinopse, categoria, logo_url, temporada, episodio, video_path_db))
            db.commit()
            return redirect(url_for('admin_cadastro_conteudo'))
        filmes = db.execute('SELECT id, titulo, categoria, "filme" as tipo FROM filmes').fetchall()
        series = db.execute('SELECT id, titulo, categoria, "serie" as tipo FROM series').fetchall()
        conteudos = list(filmes) + list(series)
        return render_template('admin/cadastro_conteudo.html', conteudos=conteudos)

    @app.route('/admin/editar/<tipo>/<int:id>', methods=['GET', 'POST'])
    @admin_required
    def admin_editar_conteudo(tipo, id):
        db = get_db()
        if tipo == 'filme':
            tabela = 'filmes'
        else:
            tabela = 'series'
        if request.method == 'POST':
            titulo = request.form['titulo']
            sinopse = request.form['sinopse']
            categoria = request.form['categoria']
            logo_url = request.form['logo_url']
            if tipo == 'serie':
                temporada = request.form['temporada']
                episodio = request.form['episodio']
                db.execute(f'UPDATE {tabela} SET titulo=?, sinopse=?, categoria=?, logo_url=?, temporada=?, episodio=? WHERE id=?',
                           (titulo, sinopse, categoria, logo_url, temporada, episodio, id))
            else:
                db.execute(f'UPDATE {tabela} SET titulo=?, sinopse=?, categoria=?, logo_url=? WHERE id=?',
                           (titulo, sinopse, categoria, logo_url, id))
            db.commit()
            return redirect(url_for('admin_cadastro_conteudo'))
        item = db.execute(f'SELECT * FROM {tabela} WHERE id=?', (id,)).fetchone()
        return render_template('admin/editar_conteudo.html', item=item, tipo=tipo)

    @app.route('/admin/excluir/<tipo>/<int:id>', methods=['POST'])
    @admin_required
    def admin_excluir_conteudo(tipo, id):
        db = get_db()
        if tipo == 'filme':
            tabela = 'filmes'
        else:
            tabela = 'series'
        # Obter caminho do vídeo para deletar o arquivo
        item = db.execute(f'SELECT video_path FROM {tabela} WHERE id = ?', (id,)).fetchone()
        if item and item['video_path']:
            try:
                video_path = os.path.join('static', item['video_path'])
                if os.path.exists(video_path):
                    os.remove(video_path)
            except Exception as e:
                print(f"Erro ao deletar arquivo: {e}")
        # Remover registros de progresso associados
        db.execute('DELETE FROM progresso WHERE conteudo_id = ? AND tipo = ?', (id, tipo))
        # Remover o conteúdo
        db.execute(f'DELETE FROM {tabela} WHERE id = ?', (id,))
        db.commit()
        return redirect(url_for('admin_cadastro_conteudo'))