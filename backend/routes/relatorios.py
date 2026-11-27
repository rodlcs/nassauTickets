import calendar
from datetime import date, datetime

from flask import Blueprint, current_app, jsonify, request

from seguranca import requer_login
from services.relatorios import gerar_relatorio

bp = Blueprint("relatorios", __name__, url_prefix="/api/relatorios")


def _responder(inicio, fim, rotulo):
    try:
        relatorio = gerar_relatorio(inicio, fim)
    except Exception:
        current_app.logger.exception("Falha ao gerar relatório")
        return jsonify({"erro": "Serviço indisponível. Tente novamente."}), 503
    return jsonify({"periodo": {"rotulo": rotulo, "de": str(inicio), "ate": str(fim)}, **relatorio})


@bp.get("/diario")
@requer_login("GESTOR")
def diario():
    """Relatório de um dia. Parâmetro opcional: ?data=AAAA-MM-DD (padrão: hoje)."""
    texto = request.args.get("data")
    try:
        dia = datetime.strptime(texto, "%Y-%m-%d").date() if texto else date.today()
    except ValueError:
        return jsonify({"erro": "Data inválida. Use o formato AAAA-MM-DD."}), 400
    return _responder(dia, dia, str(dia))


@bp.get("/mensal")
@requer_login("GESTOR")
def mensal():
    """Relatório de um mês. Parâmetro opcional: ?mes=AAAA-MM (padrão: mês atual)."""
    texto = request.args.get("mes")
    try:
        if texto:
            primeiro = datetime.strptime(texto + "-01", "%Y-%m-%d").date()
        else:
            primeiro = date.today().replace(day=1)
    except ValueError:
        return jsonify({"erro": "Mês inválido. Use o formato AAAA-MM."}), 400
    ultimo = primeiro.replace(day=calendar.monthrange(primeiro.year, primeiro.month)[1])
    return _responder(primeiro, ultimo, primeiro.strftime("%Y-%m"))