import os
from functools import lru_cache

import pypdfium2 as pdfium
import pytesseract
from PIL import Image, ImageOps

from caminhos import base_recursos


def _localizar_tesseract() -> tuple[str, str]:
    manual = os.getenv("TESSERACT_CMD", "").strip()
    if manual:
        return manual, "variável TESSERACT_CMD"

    nome = "tesseract.exe" if os.name == "nt" else "tesseract"
    embutido = base_recursos() / "vendor" / "tesseract" / nome
    if embutido.exists():
        os.environ["TESSDATA_PREFIX"] = str(embutido.parent / "tessdata")
        return str(embutido), "embutido no programa"

    return "tesseract", "instalado no sistema (PATH)"


_comando, ORIGEM = _localizar_tesseract()
pytesseract.pytesseract.tesseract_cmd = _comando


@lru_cache(maxsize=1)
def diagnostico() -> dict:
    base = {"caminho": _comando, "origem": ORIGEM}
    try:
        versao = str(pytesseract.get_tesseract_version())
        idiomas = pytesseract.get_languages(config="")
    except Exception as e:
        return {**base, "ok": False, "erro": f"{type(e).__name__}: {e}"}
    return {**base, "ok": "por" in idiomas, "versao": versao, "idiomas": idiomas}


def carregar_primeira_pagina(caminho: str) -> Image.Image:
    if caminho.lower().endswith(".pdf"):
        pdf = pdfium.PdfDocument(caminho)
        try:
            pagina = pdf[0]
            return pagina.render(scale=300 / 72).to_pil().convert("RGB")
        finally:
            pdf.close()
    return Image.open(caminho)


def preparar_imagem(imagem: Image.Image) -> Image.Image:
    return ImageOps.autocontrast(ImageOps.grayscale(imagem))


def ler_texto(caminho: str) -> str:
    imagem = preparar_imagem(carregar_primeira_pagina(caminho))
    return pytesseract.image_to_string(imagem, lang="por", config="--psm 6")