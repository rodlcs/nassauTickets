from db import get_connection


def _iso(valor):
    return valor.isoformat(timespec="seconds") if valor else None


def _formatar_duracao(segundos):
    if segundos is None:
        return None
    minutos, resto = divmod(int(round(segundos)), 60)
    return f"{minutos:02d}:{resto:02d}"


def gerar_relatorio(inicio, fim):
    """Monta o relatório das senhas emitidas entre `inicio` e `fim` (inclusive)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        periodo = (inicio, fim)

        cursor.execute(
            "SELECT COUNT(*) AS emitidas, "
            "COALESCE(SUM(estado = 'ATENDIDA'), 0) AS atendidas, "
            "COALESCE(SUM(estado = 'NAO_COMPARECEU'), 0) AS nao_compareceu, "
            "COALESCE(SUM(descartada_em IS NOT NULL), 0) AS descartadas "
            "FROM senha WHERE data_emissao BETWEEN %s AND %s",
            periodo,
        )
        totais = {chave: int(valor) for chave, valor in cursor.fetchone().items()}

        cursor.execute(
            "SELECT AVG(TIMESTAMPDIFF(SECOND, a.inicio_em, a.fim_em)) AS media "
            "FROM atendimento a JOIN senha s ON s.id = a.senha_id "
            "WHERE s.estado = 'ATENDIDA' AND s.data_emissao BETWEEN %s AND %s "
            "AND a.inicio_em IS NOT NULL AND a.fim_em IS NOT NULL",
            periodo,
        )
        media = cursor.fetchone()["media"]
        media = float(media) if media is not None else None

        cursor.execute(
            "SELECT t.sigla AS tipo, COUNT(s.id) AS emitidas, "
            "COALESCE(SUM(s.estado = 'ATENDIDA'), 0) AS atendidas "
            "FROM tipo_senha t LEFT JOIN senha s "
            "ON s.tipo_senha_id = t.id AND s.data_emissao BETWEEN %s AND %s "
            "GROUP BY t.id, t.sigla, t.ordem_prioridade "
            "ORDER BY t.ordem_prioridade",
            periodo,
        )
        por_tipo = [
            {
                "tipo": linha["tipo"],
                "emitidas": int(linha["emitidas"]),
                "atendidas": int(linha["atendidas"]),
            }
            for linha in cursor.fetchall()
        ]

        cursor.execute(
            "SELECT s.numero, t.sigla AS tipo, s.estado, s.emitida_em, "
            "a.inicio_em, g.numero AS guiche "
            "FROM senha s JOIN tipo_senha t ON t.id = s.tipo_senha_id "
            "LEFT JOIN atendimento a ON a.senha_id = s.id "
            "LEFT JOIN guiche g ON g.id = a.guiche_id "
            "WHERE s.data_emissao BETWEEN %s AND %s "
            "ORDER BY s.emitida_em, s.id",
            periodo,
        )
        detalhado = []
        for linha in cursor.fetchall():
            atendida = linha["inicio_em"] is not None
            detalhado.append(
                {
                    "numero": linha["numero"],
                    "tipo": linha["tipo"],
                    "estado": linha["estado"],
                    "emitida_em": _iso(linha["emitida_em"]),
                    # Senhas não atendidas ficam com os campos de atendimento em branco.
                    "atendida_em": _iso(linha["inicio_em"]) if atendida else None,
                    "guiche": linha["guiche"] if atendida else None,
                }
            )

        cursor.execute(
            "SELECT u.nome AS atendente, g.numero AS guiche, s.numero AS senha, "
            "a.primeira_chamada_em, a.segunda_chamada_em, a.inicio_em, a.fim_em "
            "FROM atendimento a "
            "JOIN senha s ON s.id = a.senha_id "
            "JOIN usuario u ON u.id = a.usuario_id "
            "JOIN guiche g ON g.id = a.guiche_id "
            "WHERE s.data_emissao BETWEEN %s AND %s "
            "ORDER BY a.primeira_chamada_em, a.id",
            periodo,
        )
        auditoria = [
            {
                "atendente": linha["atendente"],
                "guiche": linha["guiche"],
                "senha": linha["senha"],
                "primeira_chamada_em": _iso(linha["primeira_chamada_em"]),
                "segunda_chamada_em": _iso(linha["segunda_chamada_em"]),
                "inicio_em": _iso(linha["inicio_em"]),
                "fim_em": _iso(linha["fim_em"]),
            }
            for linha in cursor.fetchall()
        ]
    finally:
        conn.close()

    return {
        "resumo": {
            **totais,
            "tempo_medio_segundos": round(media, 1) if media is not None else None,
            "tempo_medio": _formatar_duracao(media),
        },
        "por_tipo": por_tipo,
        "detalhado": detalhado,
        "auditoria": auditoria,
    }