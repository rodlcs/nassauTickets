from flask import Flask, jsonify
from flask_cors import CORS

from db import get_connection

app = Flask(__name__)
CORS(app)


@app.get("/api/saude")
def saude():
    """Verifica se a API está no ar e se o banco responde."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tipo_senha")
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return jsonify({"status": "ok", "banco": "conectado", "tipos_de_senha": total})
    except Exception:
        # Detalhes só no log do servidor; o cliente recebe uma resposta genérica.
        app.logger.exception("Falha ao consultar o banco")
        return jsonify({"status": "erro", "banco": "indisponivel"}), 503


if __name__ == "__main__":
    app.run(debug=True, port=5000)