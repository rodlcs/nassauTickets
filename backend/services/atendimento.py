from datetime import datetime

from db import get_connection

NOME_TRAVA = "nassautickets_fila"
SEGUNDOS_ESPERA_TRAVA = 5


class GuicheInvalido(Exception):
    """Guichê inexistente ou inativo."""


class AtendimentoEmAberto(Exception):
    """O atendente ainda tem uma senha chamada ou em atendimento."""

    def __init__(self, numero, estado):
        super().__init__(numero)
        self.numero = numero
        self.estado = estado


class FilaVazia(Exception):
    """Não há senhas aguardando."""


class Ocupado(Exception):
    """Outro guichê está escolhendo a senha neste momento."""


class NaoEncontrada(Exception):
    """Senha inexistente ou que não pertence a este atendente."""


class TransicaoInvalida(Exception):
    """A ação não é permitida no estado atual da senha."""

    def __init__(self, estado):
        super().__init__(estado)
        self.estado = estado


def _historico(cursor, senha_id, anterior, novo, usuario_id, momento):
    cursor.execute(
        "INSERT INTO senha_historico "
        "(senha_id, estado_anterior, estado_novo, usuario_id, ocorrido_em) "
        "VALUES (%s, %s, %s, %s, %s)",
        (senha_id, anterior, novo, usuario_id, momento),
    )


def _ultimo_tipo_chamado(cursor, dia):
    cursor.execute(
        "SELECT t.sigla FROM atendimento a "
        "JOIN senha s ON s.id = a.senha_id "
        "JOIN tipo_senha t ON t.id = s.tipo_senha_id "
        "WHERE s.data_emissao = %s ORDER BY a.id DESC LIMIT 1",
        (dia,),
    )
    linha = cursor.fetchone()
    return linha["sigla"] if linha else None


def _primeira_da_fila(cursor, sigla, dia):
    cursor.execute(
        "SELECT s.id, s.numero FROM senha s "
        "JOIN tipo_senha t ON t.id = s.tipo_senha_id "
        "WHERE s.estado = 'AGUARDANDO' AND s.data_emissao = %s "
        "AND s.descartada_em IS NULL AND t.sigla = %s "
        "ORDER BY s.sequencia ASC LIMIT 1 FOR UPDATE",
        (dia, sigla),
    )
    return cursor.fetchone()


def chamar_proxima(usuario_id, numero_guiche):
    """Escolhe a próxima senha pelo ciclo SP -> SE|SG -> SP -> SE|SG e a chama."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    trava = False
    try:
        # Cada leitura enxerga o que os outros guichês já gravaram.
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

        # Só um guichê escolhe a senha por vez.
        cursor.execute(
            "SELECT GET_LOCK(%s, %s) AS ok", (NOME_TRAVA, SEGUNDOS_ESPERA_TRAVA)
        )
        trava = cursor.fetchone()["ok"] == 1
        if not trava:
            raise Ocupado()

        cursor.execute(
            "SELECT id FROM guiche WHERE numero = %s AND ativo = TRUE",
            (numero_guiche,),
        )
        guiche = cursor.fetchone()
        if guiche is None:
            raise GuicheInvalido(numero_guiche)

        cursor.execute(
            "SELECT s.numero, s.estado FROM atendimento a "
            "JOIN senha s ON s.id = a.senha_id "
            "WHERE a.usuario_id = %s "
            "AND s.estado IN ('CHAMADA', 'CHAMADA_NOVAMENTE', 'EM_ATENDIMENTO') "
            "LIMIT 1",
            (usuario_id,),
        )
        aberta = cursor.fetchone()
        if aberta is not None:
            raise AtendimentoEmAberto(aberta["numero"], aberta["estado"])

        agora = datetime.now()
        dia = agora.date()

        ultimo = _ultimo_tipo_chamado(cursor, dia)
        ordem = ("SE", "SG", "SP") if ultimo == "SP" else ("SP", "SE", "SG")

        escolhida = None
        tipo_escolhido = None
        for sigla in ordem:
            escolhida = _primeira_da_fila(cursor, sigla, dia)
            if escolhida is not None:
                tipo_escolhido = sigla
                break
        if escolhida is None:
            raise FilaVazia()

        cursor.execute(
            "UPDATE senha SET estado = 'CHAMADA' WHERE id = %s", (escolhida["id"],)
        )
        cursor.execute(
            "INSERT INTO atendimento "
            "(senha_id, usuario_id, guiche_id, primeira_chamada_em) "
            "VALUES (%s, %s, %s, %s)",
            (escolhida["id"], usuario_id, guiche["id"], agora),
        )
        _historico(cursor, escolhida["id"], "AGUARDANDO", "CHAMADA", usuario_id, agora)
        conn.commit()

        return {
            "id": escolhida["id"],
            "numero": escolhida["numero"],
            "tipo": tipo_escolhido,
            "estado": "CHAMADA",
            "guiche": numero_guiche,
            "chamada_em": agora.isoformat(timespec="seconds"),
        }
    finally:
        if trava:
            cursor.execute("SELECT RELEASE_LOCK(%s)", (NOME_TRAVA,))
            cursor.fetchall()
        conn.close()


def _transicao(usuario_id, senha_id, origem, novo, coluna):
    """Muda o estado de uma senha do atendente e grava o horário na coluna dada.

    `coluna` vem sempre de constantes deste arquivo, nunca do cliente.
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
        cursor.execute(
            f"UPDATE atendimento SET {coluna} = %s WHERE senha_id = %s",
            (agora, senha_id),
        )
        _historico(cursor, senha_id, linha["estado"], novo, usuario_id, agora)
        conn.commit()
        return {"id": senha_id, "estado": novo}
    finally:
        conn.close()


def iniciar(usuario_id, senha_id):
    return _transicao(
        usuario_id, senha_id, ("CHAMADA", "CHAMADA_NOVAMENTE"), "EM_ATENDIMENTO",
        "inicio_em",
    )


def finalizar(usuario_id, senha_id):
    return _transicao(
        usuario_id, senha_id, ("EM_ATENDIMENTO",), "ATENDIDA", "fim_em"
    )