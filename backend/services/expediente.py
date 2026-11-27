import os
from datetime import datetime, time
from functools import wraps

from dotenv import load_dotenv
from flask import current_app, jsonify

from db import get_connection

load_dotenv()

HORA_ABERTURA = time(7, 0)
HORA_FECHAMENTO = time(17, 0)


def expediente_ativo():
    """Se falso (só em desenvolvimento), o horário não é verificado."""
    return os.getenv("EXPEDIENTE_ATIVO", "true").strip().lower() == "true"


def dentro_do_expediente(agora=None):
    if not expediente_ativo():
        return True
    agora = agora or datetime.now()
    return HORA_ABERTURA <= agora.time() < HORA_FECHAMENTO


def descartar_pendentes(forcar=False):
    """Descarta as senhas que ficaram AGUARDANDO sem serem chamadas.

    Sempre descarta as de dias anteriores. As de hoje só são descartadas
    depois do fechamento (ou quando o gestor força o encerramento).
    """
    agora = datetime.now()
    hoje_encerrado = forcar or (
        expediente_ativo() and agora.time() >= HORA_FECHAMENTO
    )

    conn = get_connection()
    try:
        cursor = conn.cursor()
        comparador = "<=" if hoje_encerrado else "<"
        cursor.execute(
            "UPDATE senha SET descartada_em = %s "
            "WHERE estado = 'AGUARDANDO' AND descartada_em IS NULL "
            f"AND data_emissao {comparador} %s",
            (agora, agora.date()),
        )
        total = cursor.rowcount
        conn.commit()
        return total
    finally:
        conn.close()


def exige_expediente(funcao):
    """Bloqueia a rota fora do horário e aproveita para descartar pendências."""

    @wraps(funcao)
    def interna(*args, **kwargs):
        try:
            descartar_pendentes()
        except Exception:
            current_app.logger.exception("Falha ao descartar senhas pendentes")

        if not dentro_do_expediente():
            return jsonify(
                {"erro": "Fora do expediente. O atendimento funciona das 7h às 17h."}
            ), 403
        return funcao(*args, **kwargs)

    return interna