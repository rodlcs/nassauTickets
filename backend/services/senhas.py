from datetime import datetime

from mysql.connector import errors

from db import get_connection

TIPOS_VALIDOS = ("SP", "SG", "SE")
MAX_TENTATIVAS = 5


class TipoInvalido(Exception):
    """O tipo de senha informado não é SP, SG ou SE."""


def _registrar_historico(cursor, senha_id, anterior, novo, agora):
    cursor.execute(
        "INSERT INTO senha_historico (senha_id, estado_anterior, estado_novo, ocorrido_em) "
        "VALUES (%s, %s, %s, %s)",
        (senha_id, anterior, novo, agora),
    )


def emitir_senha(sigla):
    """Emite uma senha no padrão YYMMDD-PPSQ e a deixa AGUARDANDO."""
    sigla = (sigla or "").upper()
    if sigla not in TIPOS_VALIDOS:
        raise TipoInvalido(sigla)

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM tipo_senha WHERE sigla = %s", (sigla,))
        tipo = cursor.fetchone()
        if tipo is None:
            raise TipoInvalido(sigla)

        agora = datetime.now()

        for _ in range(MAX_TENTATIVAS):
            cursor.execute(
                "SELECT COALESCE(MAX(sequencia), 0) + 1 AS proxima "
                "FROM senha WHERE data_emissao = %s AND tipo_senha_id = %s",
                (agora.date(), tipo["id"]),
            )
            sequencia = cursor.fetchone()["proxima"]
            numero = f"{agora:%y%m%d}-{sigla}{sequencia:03d}"

            try:
                cursor.execute(
                    "INSERT INTO senha (numero, tipo_senha_id, data_emissao, sequencia, "
                    "estado, emitida_em) VALUES (%s, %s, %s, %s, 'EMITIDA', %s)",
                    (numero, tipo["id"], agora.date(), sequencia, agora),
                )
            except errors.IntegrityError:
                # Outro cliente pegou esse número ao mesmo tempo: tenta o próximo.
                conn.rollback()
                continue

            senha_id = cursor.lastrowid
            _registrar_historico(cursor, senha_id, None, "EMITIDA", agora)

            cursor.execute(
                "UPDATE senha SET estado = 'AGUARDANDO' WHERE id = %s", (senha_id,)
            )
            _registrar_historico(cursor, senha_id, "EMITIDA", "AGUARDANDO", agora)

            conn.commit()
            return {
                "id": senha_id,
                "numero": numero,
                "tipo": sigla,
                "estado": "AGUARDANDO",
                "emitida_em": agora.isoformat(timespec="seconds"),
            }

        raise RuntimeError("Não foi possível gerar um número de senha.")
    finally:
        conn.close()