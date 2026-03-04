from flask import request, session, jsonify
from models import get_db

def salvar_progresso(usuario_id, conteudo_id, tipo, temporada, episodio, tempo_assistido, duracao_total):
    db = get_db()
    db.execute('''
        INSERT INTO progresso (usuario_id, conteudo_id, tipo, temporada, episodio, tempo_assistido, duracao_total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(usuario_id, conteudo_id, tipo, temporada, episodio) DO UPDATE SET tempo_assistido=excluded.tempo_assistido
    ''', (usuario_id, conteudo_id, tipo, temporada, episodio, tempo_assistido, duracao_total))
    db.commit()

def obter_progresso(usuario_id, conteudo_id, tipo, temporada=None, episodio=None):
    db = get_db()
    row = db.execute('''
        SELECT tempo_assistido FROM progresso
        WHERE usuario_id=? AND conteudo_id=? AND tipo=?
        AND (temporada IS ? OR ? IS NULL) AND (episodio IS ? OR ? IS NULL)
    ''', (usuario_id, conteudo_id, tipo, temporada, temporada, episodio, episodio)).fetchone()
    return row['tempo_assistido'] if row else 0