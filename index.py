"""
INICIADOR AUTOMÁTICO do jogo Pedra, Papel e Tesoura.

Basta rodar este arquivo (ou dar dois cliques em INICIAR.bat / iniciar.command).
Ele faz tudo sozinho:
  1. instala o Flask, se ainda não estiver instalado;
  2. escolhe uma porta livre;
  3. liga o servidor;
  4. abre o jogo no seu navegador.
"""
import os
import socket
import subprocess
import sys
import threading
import webbrowser

PASTA = os.path.dirname(os.path.abspath(__file__))
os.chdir(PASTA)  # garante que o Flask ache as pastas templates/ e static/


def garantir_flask():
    """Instala as dependências (requirements.txt) se o Flask não existir."""
    try:
        import flask  # noqa: F401
    except ImportError:
        print("Flask não encontrado. Instalando, aguarde...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
            )
        except subprocess.CalledProcessError:
            print("\nNão consegui instalar o Flask automaticamente.")
            print("Tente manualmente:  pip install -r requirements.txt")
            input("\nPressione ENTER para sair...")
            sys.exit(1)


def achar_porta_livre(inicio=5000, tentativas=20):
    """Procura uma porta que não esteja em uso (a 5000 às vezes está ocupada)."""
    for porta in range(inicio, inicio + tentativas):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", porta)) != 0:
                return porta
    return inicio


def main():
    garantir_flask()
    from app import app  # importa só depois de garantir que o Flask existe

    porta = achar_porta_livre()
    url = f"http://127.0.0.1:{porta}"

    # espera o servidor ligar (1,5 s) e então abre o navegador
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    print("=" * 50)
    print(f" Jogo rodando em: {url}")
    print(" Para encerrar: feche esta janela ou aperte Ctrl+C")
    print("=" * 50)

    app.run(host="127.0.0.1", port=porta, debug=False)


if __name__ == "__main__":
    main()
