import os
from functools import wraps

from dotenv import load_dotenv
from flask import g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

load_dotenv()

TOKEN_VALIDADE_SEGUNDOS = 8 * 60 * 60  # 8 horas


def _serializador():
    chave = os.getenv("SECRET_KEY")
    if not chave:
        raise RuntimeError("SECRET_KEY não configurada no .env")
    return URLSafeTimedSerializer(chave, salt="nassautickets-auth")


def gerar_token(usuario_id, perfil):
    """Gera um token assinado com o id e o perfil do usuário."""
    return _serializador().dumps({"id": usuario_id, "perfil": perfil})


def requer_login(perfil=None):
    """Protege uma rota. Com perfil='GESTOR', só o gestor acessa.

    O gestor também é atendente, então uma rota sem perfil aceita os dois.
    """

    def decorador(funcao):
        @wraps(funcao)
        def interna(*args, **kwargs):
            cabecalho = request.headers.get("Authorization", "")
            if not cabecalho.startswith("Bearer "):
                return jsonify({"erro": "Não autenticado."}), 401

            token = cabecalho[len("Bearer "):]
            try:
                dados = _serializador().loads(token, max_age=TOKEN_VALIDADE_SEGUNDOS)
            except (SignatureExpired, BadSignature):
                return jsonify({"erro": "Sessão inválida ou expirada."}), 401

            if perfil and dados.get("perfil") != perfil:
                return jsonify({"erro": "Acesso negado."}), 403

            g.usuario = dados
            return funcao(*args, **kwargs)

        return interna

    return decorador