from flask import Blueprint, current_app, jsonify, request

from services.expediente import exige_expediente
from services.senhas import TipoInvalido, emitir_senha

bp = Blueprint("senhas", __name__, url_prefix="/api/senhas")


@bp.post("")
@exige_expediente
def criar():
    """Emite uma nova senha. Corpo esperado: {"tipo": "SP" | "SG" | "SE"}."""
    dados = request.get_json(silent=True) or {}
    try:
        senha = emitir_senha(dados.get("tipo"))
    except TipoInvalido:
        return jsonify({"erro": "Tipo de senha inválido. Use SP, SG ou SE."}), 400
    except Exception:
        current_app.logger.exception("Falha ao emitir senha")
        return jsonify({"erro": "Serviço indisponível. Tente novamente."}), 503
    return jsonify(senha), 201