from flask import Blueprint, current_app, jsonify

from seguranca import requer_login
from services import expediente as exp

bp = Blueprint("expediente", __name__, url_prefix="/api/expediente")


@bp.get("")
def situacao():
    """Informa se o laboratório está aberto (usado pelo totem e pelo painel)."""
    return jsonify(
        {
            "aberto": exp.dentro_do_expediente(),
            "abertura": exp.HORA_ABERTURA.strftime("%H:%M"),
            "fechamento": exp.HORA_FECHAMENTO.strftime("%H:%M"),
        }
    )


@bp.post("/encerrar")
@requer_login("GESTOR")
def encerrar():
    """Descarta as senhas que sobraram na fila (só o gestor)."""
    try:
        total = exp.descartar_pendentes(forcar=True)
    except Exception:
        current_app.logger.exception("Falha ao encerrar o expediente")
        return jsonify({"erro": "Serviço indisponível. Tente novamente."}), 503
    return jsonify({"descartadas": total})