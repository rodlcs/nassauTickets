from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.security import check_password_hash

from db import get_connection
from seguranca import gerar_token, requer_login

bp = Blueprint("login", __name__, url_prefix="/api")


@bp.post("/login")
def login():
    """Autentica o atendente. Corpo: {"login": "...", "senha": "..."}."""
    dados = request.get_json(silent=True) or {}
    login_informado = (dados.get("login") or "").strip()
    senha = dados.get("senha") or ""

    if not login_informado or not senha:
        return jsonify({"erro": "Informe login e senha."}), 400

    try:
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, nome, senha_hash, perfil FROM usuario "
                "WHERE login = %s AND ativo = TRUE",
                (login_informado,),
            )
            usuario = cursor.fetchone()
        finally:
            conn.close()
    except Exception:
        current_app.logger.exception("Falha ao consultar usuário")
        return jsonify({"erro": "Serviço indisponível. Tente novamente."}), 503

    # Mensagem única para não revelar se o login existe.
    if usuario is None or not check_password_hash(usuario["senha_hash"], senha):
        return jsonify({"erro": "Login ou senha incorretos."}), 401

    return jsonify(
        {
            "token": gerar_token(usuario["id"], usuario["perfil"]),
            "usuario": {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "perfil": usuario["perfil"],
            },
        }
    )


@bp.get("/eu")
@requer_login()
def eu():
    """Devolve os dados da sessão atual (usado para testar o login)."""
    return jsonify(g.usuario)