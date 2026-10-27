import os
import shutil
import tempfile

from dotenv import load_dotenv

load_dotenv()  

from fastapi import FastAPI, File, HTTPException, UploadFile  
from fastapi.middleware.cors import CORSMiddleware  

from extractor import extrair_campos  
from ocr import ler_texto  

app = FastAPI(title="Leitor de capas de processo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGIN", "http://localhost:3000")],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

EXTENSOES_OK = (".pdf", ".png", ".jpg", ".jpeg")


@app.get("/health")
def health():
    """Rota simples para verificar se o servidor está de pé."""
    return {"status": "ok"}


@app.post("/extract")
def extract(arquivo: UploadFile = File(...), debug: bool = False):
    nome = (arquivo.filename or "").lower()
    if not nome.endswith(EXTENSOES_OK):
        raise HTTPException(400, "Envie um PDF, PNG ou JPG.")

    sufixo = os.path.splitext(nome)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
        shutil.copyfileobj(arquivo.file, tmp)
        caminho = tmp.name

    try:
        texto = ler_texto(caminho)
        resposta = {"campos": extrair_campos(texto)}
        if debug:
            resposta["texto_bruto"] = texto
        return resposta
    finally:
        os.remove(caminho)