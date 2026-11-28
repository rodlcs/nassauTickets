from datetime import date, datetime

from db import get_connection
from services.atendimento import NaoEncontrada, TransicaoInvalida, _historico


def _mudar_estado(usuario_id, senha_id, origem, novo, coluna=None):
    """Muda o estado de uma senha do atendente.

    Se `coluna` for informada, grava o horário nela. O nome da coluna vem
    sempre de constantes deste arquivo, nunca do cliente.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(
            "SELECT s.estado FROM senha s "
            "JOIN atendimento a ON a.senha_id = s.id "
            "WHERE s.id = %s AND a.usuario_id = %s FOR UPDATE",
            (senha_id, usuario_id),
        )
        linha = cursor.fetchone()
        if linha is None:
            raise NaoEncontrada()
        if linha["estado"] not in origem:
            raise TransicaoInvalida(linha["estado"])

        agora = datetime.now()
        cursor.execute("UPDATE senha SET estado = %s WHERE id = %s", (novo, senha_id))
        if coluna:
            cursor.execute(
                f"UPDATE atendimento SET {coluna} = %s WHERE senha_id = %s",
                (agora, senha_id),
            )
        _historico(cursor, senha_id, linha["estado"], novo, usuario_id, agora)
        conn.commit()
        return {"id": senha_id, "estado": novo}
    finally:
        conn.close()


def chamar_novamente(usuario_id, senha_id):
    """Segunda e última chamada da senha."""
    return _mudar_estado(
        usuario_id, senha_id, ("CHAMADA",), "CHAMADA_NOVAMENTE", "segunda_chamada_em"
    )


def nao_compareceu(usuario_id, senha_id):
    """Abandono: o cliente não apareceu após as duas chamadas."""
    return _mudar_estado(
        usuario_id, senha_id, ("CHAMADA_NOVAMENTE",), "NAO_COMPARECEU"
    )


def atendimento_atual(usuario_id):
    """A senha que o atendente tem em aberto (chamada ou em atendimento), se houver."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT s.id, s.numero, t.sigla AS tipo, s.estado, g.numero AS guiche "
            "FROM atendimento a "
            "JOIN senha s ON s.id = a.senha_id "
            "JOIN tipo_senha t ON t.id = s.tipo_senha_id "
            "JOIN guiche g ON g.id = a.guiche_id "
            "WHERE a.usuario_id = %s "
            "AND s.estado IN ('CHAMADA', 'CHAMADA_NOVAMENTE', 'EM_ATENDIMENTO') "
            "ORDER BY a.id DESC LIMIT 1",
            (usuario_id,),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def painel(limite=5):
    """As últimas senhas chamadas hoje, da mais recente para a mais antiga."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT s.numero, t.sigla AS tipo, g.numero AS guiche, s.estado, "
            "COALESCE(a.segunda_chamada_em, a.primeira_chamada_em) AS chamada_em "
            "FROM atendimento a "
            "JOIN senha s ON s.id = a.senha_id "
            "JOIN tipo_senha t ON t.id = s.tipo_senha_id "
            "JOIN guiche g ON g.id = a.guiche_id "
            "WHERE s.data_emissao = %s "
            "ORDER BY chamada_em DESC, a.id DESC LIMIT %s",
            (date.today(), limite),
        )
        linhas = cursor.fetchall()
    finally:
        conn.close()

    return [
        {
            "numero": linha["numero"],
            "tipo": linha["tipo"],
            "guiche": linha["guiche"],
            "estado": linha["estado"],
            "ultima_chamada": linha["estado"] == "CHAMADA_NOVAMENTE",
            "chamada_em": linha["chamada_em"].isoformat(timespec="seconds"),
        }
        for linha in linhas
    ]