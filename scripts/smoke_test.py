#!/usr/bin/env python3
"""
Uso:  python scripts/smoke_test.py caminho\\para\\LeitorDeProcessos.exe
Falha (código 1) com uma mensagem clara se algo estiver errado.
"""
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx
from PIL import Image, ImageDraw, ImageFont

URL = "http://127.0.0.1:8000"


def falhar(msg: str) -> None:
    print(f"FALHOU: {msg}")
    sys.exit(1)


def fonte(tamanho: int):
    for nome in ("arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            pass
    return ImageFont.load_default(size=tamanho)


def criar_capa(destino: Path) -> None:
    """Capa FICTÍCIA (nenhum dado real)."""
    img = Image.new("RGB", (1500, 700), "white")
    d = ImageDraw.Draw(img)
    linhas = [
        "Processo do tipo Técnico registrado sob nº 12345/2020", "",
        "Objetivo: Cadastro Ambiental Rural - CAR - Alteração - Cadastro A",
        "Interessado: Fulano de Tal - CPF/CNPJ: 000.000.000-00", "",
        "Código: 98765 Empreendimento: Sítio Teste CNPJ",
        "Checagem de Itens: 11111 Req", "Local e data:", "",
        "Domingos Martins - ES, 30/12/2020",
    ]
    y = 40
    for linha in linhas:
        d.text((50, y), linha, fill="black", font=fonte(34))
        y += 60
    img.save(destino)


def esperar_servidor() -> None:
    for _ in range(120):  # até ~60 s
        try:
            if httpx.get(f"{URL}/api/health", timeout=2).json().get("app") == "leitor-processos":
                return
        except Exception:
            pass
        time.sleep(0.5)
    falhar("o servidor não respondeu em 60 segundos.")


def main() -> None:
    if len(sys.argv) != 2:
        falhar("uso: python scripts/smoke_test.py <caminho do LeitorDeProcessos.exe>")
    exe = sys.argv[1]

    processo = subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        esperar_servidor()
        print("1. servidor no ar")

        pagina = httpx.get(f"{URL}/", timeout=10)
        if pagina.status_code != 200 or "<html" not in pagina.text.lower():
            falhar(f"o site não foi servido (status {pagina.status_code}).")
        print("2. site servido")

        diag = httpx.get(f"{URL}/api/diagnostico", timeout=30).json()
        if not diag.get("ok"):
            falhar(f"Tesseract com problema: {diag}")
        if diag.get("origem") != "embutido no programa":
            falhar(f"não está usando o Tesseract embutido: {diag}")
        print(f"3. Tesseract embutido OK (versão {diag.get('versao')})")

        with tempfile.TemporaryDirectory() as tmp:
            capa = Path(tmp) / "capa.png"
            criar_capa(capa)
            with open(capa, "rb") as f:
                resp = httpx.post(f"{URL}/api/extract", files={"arquivo": ("capa.png", f, "image/png")}, timeout=120)
        if resp.status_code != 200:
            falhar(f"leitura da capa deu erro {resp.status_code}: {resp.text}")
        campos = resp.json()["campos"]

        esperado = {"numero": "12345", "ano": "2020", "codigo": "98765",
                    "cpf": "000.000.000-00", "data": "30/12/2020"}
        for chave, valor in esperado.items():
            if campos.get(chave) != valor:
                falhar(f"campo '{chave}': esperado '{valor}', veio '{campos.get(chave)}'. Campos: {campos}")
        print("4. leitura da capa OK")

        # Nomes variam um pouco conforme a fonte: só avisamos, não reprovamos.
        for chave, valor in {"pessoa": "Fulano de Tal", "origem": "Domingos Martins"}.items():
            if campos.get(chave) != valor:
                print(f"   aviso: '{chave}' veio '{campos.get(chave)}' (esperado '{valor}')")

        print("TUDO CERTO")
    finally:
        processo.terminate()


if __name__ == "__main__":
    main()