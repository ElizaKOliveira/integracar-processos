import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageOps


_tess_cmd = os.getenv("TESSERACT_CMD")
if _tess_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tess_cmd


def carregar_primeira_pagina(caminho: str) -> Image.Image:

    if caminho.lower().endswith(".pdf"):
        documento = fitz.open(caminho)
        try:
            pagina = documento.load_page(0)
            pixmap = pagina.get_pixmap(dpi=300)
            return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        finally:
            documento.close()

    return Image.open(caminho)


def preparar_imagem(imagem: Image.Image) -> Image.Image:
    #Pré-processamento. Otimização da imagem escaneada.
    cinza = ImageOps.grayscale(imagem)
    return ImageOps.autocontrast(cinza)


def ler_texto(caminho: str) -> str:
    imagem = preparar_imagem(carregar_primeira_pagina(caminho))
    return pytesseract.image_to_string(imagem, lang="por", config="--psm 6")