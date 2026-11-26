from flask import Blueprint, current_app, g, jsonify, request

from seguranca import requer_login
from services import atendimento as svc

bp = Blueprint("atendimento", __name__, url_prefix="/api")


@bp.post("/chamadas/proxima")
@requer_login()
def chamar_proxima():
    """Chama a próxima senha. Corpo: {"guiche": 1}."""
    dados = request.get_json(silent=True) or {}
    try:
        numero_guiche = int(dados.get("guiche"))
    except (TypeError, ValueError):
        return jsonify({"erro": "Informe o número do guichê."}), 400

    try:
        senha = svc.chamar_proxima(g.usuario["id"], numero_guiche)
    except svc.GuicheInvalido:
        return jsonify({"erro": "Guichê inválido ou inativo."}), 400
    except svc.AtendimentoEmAberto as e:
        return jsonify(
            {"erro": f"Finalize a senha {e.numero} ({e.estado}) antes de chamar a próxima."}
        ), 409
    except svc.FilaVazia:
        return jsonify({"erro": "Não há senhas aguardando."}), 404
    except svc.Ocupado:
        return jsonify({"erro": "Sistema ocupado. Tente novamente."}), 503
    except Exception:
        current_app.logger.exception("Falha ao chamar próxima senha")
        return jsonify({"erro": "Serviço indisponível. Tente novamente."}), 503
    return jsonify(senha)


def _executar(acao, senha_id):
    try:
        resultado = acao(g.usuario["id"], senha_id)
    except svc.NaoEncontrada:
        return jsonify({"erro": "Senha não encontrada para este atendente."}), 404
    except svc.TransicaoInvalida as e:
        return jsonify({"erro": f"Ação não permitida para uma senha {e.estado}."}), 409
    except Exception:
        current_app.logger.exception("Falha ao atualizar atendimento")
        return jsonify({"erro": "Serviço indisponível. Tente novamente."}), 503
    return jsonify(resultado)


@bp.post("/atendimentos/<int:senha_id>/iniciar")
@requer_login()
def iniciar(senha_id):
    return _executar(svc.iniciar, senha_id)


@bp.post("/atendimentos/<int:senha_id>/finalizar")
@requer_login()
def finalizar(senha_id):
    return _executar(svc.finalizar, senha_id)