from flask import request, session, jsonify
from models import get_db

@app.route('/api/progresso')
def get_progresso():
    usuario_id = session['usuario_id']
    tipo = request.args.get('tipo')
    conteudo_id = request.args.get('id')
    temporada = request.args.get('temp')
    episodio = request.args.get('ep')
    db = get_db()
    prog = db.execute('''
        SELECT tempo_assistido FROM progresso
        WHERE usuario_id=? AND conteudo_id=? AND tipo=?
        AND (temporada IS ? OR ? IS NULL) AND (episodio IS ? OR ? IS NULL)
    ''', (usuario_id, conteudo_id, tipo, temporada, temporada, episodio, episodio)).fetchone()
    return jsonify({'tempo': prog['tempo_assistido'] if prog else 0})

@app.route('/api/salvar_progresso', methods=['POST'])
def salvar_progresso():
    data = request.get_json()
    usuario_id = session['usuario_id']
    db = get_db()
    db.execute('''
        INSERT INTO progresso (usuario_id, conteudo_id, tipo, temporada, episodio, tempo_assistido, duracao_total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(usuario_id, conteudo_id, tipo, temporada, episodio) DO UPDATE SET tempo_assistido=excluded.tempo_assistido
    ''', (usuario_id, data['id'], data['tipo'], data.get('temporada'), data.get('episodio'), data['tempo_assistido'], data['duracao_total']))
    db.commit()
    return '', 204