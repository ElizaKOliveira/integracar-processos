import json
import logging
import logging.handlers
import multiprocessing
import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

HOST = "127.0.0.1"  
PORTA_PADRAO = 8000
EMPACOTADO = getattr(sys, "frozen", False)


def porta_livre(porta: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((HOST, porta)) != 0


def e_nosso_servidor(porta: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://{HOST}:{porta}/api/health", timeout=1) as r:
            return json.load(r).get("app") == "leitor-processos"
    except Exception:
        return False


def escolher_porta() -> tuple[int, bool]:
    if porta_livre(PORTA_PADRAO):
        return PORTA_PADRAO, False
    if e_nosso_servidor(PORTA_PADRAO):
        return PORTA_PADRAO, True 
    for porta in range(PORTA_PADRAO + 1, PORTA_PADRAO + 20):
        if porta_livre(porta):
            return porta, False
    raise RuntimeError("Nenhuma porta livre encontrada entre 8000 e 8019.")


def abrir_quando_pronto(porta: int) -> None:
    for _ in range(100):
        if e_nosso_servidor(porta):
            webbrowser.open(f"http://{HOST}:{porta}")
            return
        time.sleep(0.3)


def configurar_log() -> None:
    import config

    pasta = config.pasta_config() / "logs"
    pasta.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        logging.handlers.RotatingFileHandler(
            pasta / "leitor.log", maxBytes=1_000_000, backupCount=2, encoding="utf-8")
    ]
    if sys.stdout is not None:
        handlers.append(logging.StreamHandler(sys.stdout))
    logging.basicConfig(level=logging.INFO, handlers=handlers,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")


def mensagem_inicial(url: str) -> None:
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW("Leitor de Processos")  # type: ignore[attr-defined]
        except Exception:
            pass
    print("=" * 62)
    print("  Leitor de Processos")
    print(f"  Aberto em: {url}")
    print("  Mantenha esta janela aberta enquanto estiver usando.")
    print("  Para ENCERRAR o programa, feche esta janela.")
    print("=" * 62, flush=True)


def main() -> None:
    porta, ja_rodando = escolher_porta()
    url = f"http://{HOST}:{porta}"
    if ja_rodando:
        webbrowser.open(url)
        return

    if EMPACOTADO:
        configurar_log()
    mensagem_inicial(url)

    threading.Thread(target=abrir_quando_pronto, args=(porta,), daemon=True).start()

    import uvicorn
    from main import app  

    config_log = None if EMPACOTADO else uvicorn.config.LOGGING_CONFIG
    uvicorn.run(app, host=HOST, port=porta, log_config=config_log)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()