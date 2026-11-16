#!/usr/bin/env python3
"""
Requisito: 7-Zip.
  Fedora:          sudo dnf install 7zip
  Ubuntu/Debian:   sudo apt install 7zip   (ou: sudo apt install p7zip-full)
  Windows:         7-Zip no PATH55
"""
import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import date
from pathlib import Path

URL_INSTALADOR = "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.3/tesseract-ocr-w64-setup-5.5.3.20260724.exe"
SHA256_INSTALADOR = "bee9e3434bd94fd65387d9be28cd467a41f61b1275383b55b0f59a1331270ae4"
URL_POR = "https://github.com/tesseract-ocr/tessdata_fast/raw/main/por.traineddata"


RAIZ = Path(__file__).resolve().parent.parent


def achar_7zip() -> str:
    for nome in ("7zz", "7z", "7za"):
        caminho = shutil.which(nome)
        if caminho:
            return caminho
    sys.exit("7-Zip não encontrado. Instale (veja o início deste arquivo) e rode de novo.")


def baixar(url: str, destino: Path) -> None:
    print(f"Baixando {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (preparar_tesseract)"})
    with urllib.request.urlopen(req, timeout=120) as resposta, open(destino, "wb") as f:
        shutil.copyfileobj(resposta, f)


def sha256(arquivo: Path) -> str:
    h = hashlib.sha256()
    with open(arquivo, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def achar(pasta: Path, nome: str) -> Path | None:
    for item in pasta.iterdir():
        if item.name.lower() == nome.lower():
            return item
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url-instalador", default=URL_INSTALADOR)
    ap.add_argument("--sha256", help="Hash esperado do instalador (opcional, mas recomendado)")
    ap.add_argument("--destino", default=str(RAIZ / "backend" / "vendor" / "tesseract"))
    args = ap.parse_args()

    sete_zip = achar_7zip()
    destino = Path(args.destino)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        instalador = tmp / "setup.exe"
        baixar(args.url_instalador, instalador)

        hash_instalador = sha256(instalador)
        print(f"SHA-256 do instalador: {hash_instalador}")
        esperado = args.sha256 or (
            SHA256_INSTALADOR if args.url_instalador == URL_INSTALADOR else None
        )
        if esperado and esperado.lower() != hash_instalador:
            sys.exit("O hash do instalador não confere com o esperado. Abortando.")

        extraido = tmp / "extraido"
        print("Extraindo com 7-Zip...")
        subprocess.run([sete_zip, "x", "-y", f"-o{extraido}", str(instalador)],
                       check=True, stdout=subprocess.DEVNULL)

        exes = [p for p in extraido.rglob("*") if p.is_file() and p.name.lower() == "tesseract.exe"]
        if not exes:
            sys.exit("Não achei tesseract.exe dentro do instalador. O formato do instalador pode ter mudado.")
        origem = exes[0].parent

        if destino.exists():
            shutil.rmtree(destino)
        (destino / "tessdata").mkdir(parents=True)

        shutil.copy2(exes[0], destino / "tesseract.exe")
        n_dlls = 0
        for item in origem.iterdir():
            if item.is_file() and item.suffix.lower() == ".dll":
                shutil.copy2(item, destino / item.name)
                n_dlls += 1

        tessdata_origem = achar(origem, "tessdata")
        if tessdata_origem:
            for sub in ("configs", "tessconfigs"):
                pasta = achar(tessdata_origem, sub)
                if pasta and pasta.is_dir():
                    shutil.copytree(pasta, destino / "tessdata" / sub)

        baixar(URL_POR, destino / "tessdata" / "por.traineddata")

        (destino / "ORIGEM.txt").write_text(
            f"Gerado em {date.today()}\nInstalador: {args.url_instalador}\nSHA-256: {hash_instalador}\n"
            f"Idioma: {URL_POR}\n", encoding="utf-8")

    problemas = []
    if not (destino / "tesseract.exe").is_file():
        problemas.append("tesseract.exe ausente")
    if n_dlls < 3:
        problemas.append(f"poucas DLLs copiadas ({n_dlls})")
    por = destino / "tessdata" / "por.traineddata"
    if not por.is_file() or por.stat().st_size < 500_000:
        problemas.append("por.traineddata ausente ou pequeno demais")
    if problemas:
        sys.exit("Algo saiu errado: " + "; ".join(problemas))

    total = sum(f.stat().st_size for f in destino.rglob("*") if f.is_file()) / 1_000_000
    print(f"\nPronto: {destino}\n  {n_dlls} DLLs, idioma por, {total:.0f} MB no total.")


if __name__ == "__main__":
    main()