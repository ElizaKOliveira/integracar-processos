#!/usr/bin/env python3
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
    for _ in range(120):  
        try:
            if httpx.get(f"{URL}/api/health", timeout=2).json().get("app") == "leitor-processos":
                return
        except Exception:
            pass
        time.sleep(0.5)
    falhar("o servidor não respondeu em 60 segundos.")


def conferir_campos(origem: str, campos: dict) -> None:
    esperado = {
        "processo_simlam": "12345/2020",
        "cpf": "000.000.000-00",
        "data": "30/12/2020",
    }
    for chave, valor in esperado.items():
        if campos.get(chave) != valor:
            falhar(f"[{origem}] campo '{chave}': esperado '{valor}', veio '{campos.get(chave)}'. Campos: {campos}")

    if "98765" not in campos.get("nome_arquivo", ""):
        falhar(f"[{origem}] código 98765 não apareceu em 'nome_arquivo'. Campos: {campos}")

    nome = campos.get("interessado")
    if nome != "Fulano de Tal":
        print(f"   aviso: nome do interessado veio '{nome}' (esperado 'Fulano de Tal')")
    if campos.get("origem") != "Domingos Martins":
        print(f"   aviso: origem veio '{campos.get('origem')}' (esperado 'Domingos Martins')")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  
    except Exception:
        pass

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
            png = Path(tmp) / "capa.png"
            pdf = Path(tmp) / "capa.pdf"
            criar_capa(png)
            Image.open(png).convert("RGB").save(pdf, "PDF", resolution=300)

            for arquivo, tipo in ((png, "image/png"), (pdf, "application/pdf")):
                with open(arquivo, "rb") as f:
                    resp = httpx.post(
                        f"{URL}/api/extract",
                        files={"arquivo": (arquivo.name, f, tipo)},
                        timeout=120,
                    )
                if resp.status_code != 200:
                    falhar(f"leitura de {arquivo.name} deu erro {resp.status_code}: {resp.text}")
                conferir_campos(arquivo.name, resp.json()["campos"])
                print(f"4. leitura de {arquivo.suffix} OK")

        print("TUDO CERTO")
    finally:
        processo.terminate()


if __name__ == "__main__":
    main()