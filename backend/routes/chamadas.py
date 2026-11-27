from flask import Blueprint, current_app, g, jsonify

from seguranca import requer_login
from services import chamadas as svc
from services.atendimento import NaoEncontrada, TransicaoInvalida

bp = Blueprint("chamadas", __name__, url_prefix="/api")


def _executar(acao, senha_id):
    try:
        resultado = acao(g.usuario["id"], senha_id)
    except NaoEncontrada:
        return jsonify({"erro": "Senha não encontrada para este atendente."}), 404
    except TransicaoInvalida as e:
        return jsonify({"erro": f"Ação não permitida para uma senha {e.estado}."}), 409
    except Exception:
        current_app.logger.exception("Falha ao atualizar atendimento")
        return jsonify({"erro": "Serviço indisponível. Tente novamente."}), 503
    return jsonify(resultado)


@bp.post("/atendimentos/<int:senha_id>/rechamar")
@requer_login()
def rechamar(senha_id):
    return _executar(svc.chamar_novamente, senha_id)


@bp.post("/atendimentos/<int:senha_id>/nao-compareceu")
@requer_login()
def nao_compareceu(senha_id):
    return _executar(svc.nao_compareceu, senha_id)


@bp.get("/painel")
def painel():
    """Painel público: só número, tipo e guichê, sem dados pessoais."""
    try:
        senhas = svc.painel()
    except Exception:
        current_app.logger.exception("Falha ao montar o painel")
        return jsonify({"erro": "Painel indisponível."}), 503
    return jsonify({"senhas": senhas})