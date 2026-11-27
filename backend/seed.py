"""Cadastros iniciais: guichês e usuário gestor.

Execute uma vez, na pasta backend:  python seed.py
A senha é digitada no terminal e nunca fica gravada em arquivo.
"""
import getpass

from werkzeug.security import generate_password_hash

from db import get_connection

QUANTIDADE_GUICHES = 3  # Proposta: o número real de guichês é um ponto em aberto.


def main():
    conn = get_connection()
    try:
        cursor = conn.cursor()

        for numero in range(1, QUANTIDADE_GUICHES + 1):
            cursor.execute("INSERT IGNORE INTO guiche (numero) VALUES (%s)", (numero,))

        cursor.execute("SELECT COUNT(*) FROM usuario WHERE perfil = 'GESTOR'")
        if cursor.fetchone()[0] > 0:
            print("Já existe um gestor cadastrado. Guichês conferidos.")
        else:
            nome = input("Nome do gestor: ").strip()
            login = input("Login: ").strip()
            senha = getpass.getpass("Senha (mínimo 8 caracteres): ")
            repeticao = getpass.getpass("Repita a senha: ")

            if not nome or not login or len(senha) < 8:
                print("Nome e login são obrigatórios e a senha precisa de 8+ caracteres.")
                return
            if senha != repeticao:
                print("As senhas não coincidem.")
                return

            cursor.execute(
                "INSERT INTO usuario (nome, login, senha_hash, perfil) "
                "VALUES (%s, %s, %s, 'GESTOR')",
                (nome, login, generate_password_hash(senha)),
            )
            print("Gestor cadastrado.")

        conn.commit()
        print(f"Guichês de 1 a {QUANTIDADE_GUICHES} disponíveis.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()