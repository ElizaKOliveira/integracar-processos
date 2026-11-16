import logging
import os
import shutil
import tempfile
from pathlib import Path

import sys

if not getattr(sys, "frozen", False):
    from dotenv import load_dotenv
    load_dotenv()

from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from starlette.middleware.trustedhost import TrustedHostMiddleware  # noqa: E402

import re
import subprocess
from urllib.parse import urlparse

from fastapi.responses import JSONResponse  # noqa: E402
from pydantic import BaseModel  # noqa: E402

import config  # noqa: E402
from armazenamento import ErroDeGravacao, Linha, gravar, testar_conexao  # noqa: E402
from extractor import extrair_campos  # noqa: E402

from caminhos import base_recursos  # noqa: E402
from ocr import diagnostico, ler_texto  # noqa: E402

log = logging.getLogger("leitor")
BASE = base_recursos()
EXTENSOES_OK = (".pdf", ".png", ".jpg", ".jpeg", ".webp")

app = FastAPI(title="Leitor de capas de processo")


app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
@app.middleware("http")
async def so_origem_local(request, call_next):
    origem = request.headers.get("origin")
    if request.method not in ("GET", "HEAD", "OPTIONS") and origem:
        if urlparse(origem).hostname not in ("127.0.0.1", "localhost"):
            return JSONResponse({"detail": "Origem não permitida."}, status_code=403)
    return await call_next(request)

if os.getenv("ALLOWED_ORIGIN"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[os.environ["ALLOWED_ORIGIN"]],
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
    )

api = APIRouter(prefix="/api")


@api.get("/health")
def health():
    return {"status": "ok", "app": "leitor-processos"}


@api.post("/extract")
def extract(arquivo: UploadFile = File(...), debug: bool = False):
    nome = (arquivo.filename or "").lower()
    if not nome.endswith(EXTENSOES_OK):
        raise HTTPException(400, "Envie um PDF, PNG, JPG ou WEBP.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(nome)[1]) as tmp:
        shutil.copyfileobj(arquivo.file, tmp)
        caminho = tmp.name

    try:
        texto = ler_texto(caminho)
        resposta = {"campos": extrair_campos(texto)}
        if debug:
            resposta["texto_bruto"] = texto  
        return resposta
    except Exception:
        log.exception("Falha ao ler o documento")
        raise HTTPException(500, "Não consegui ler este documento. Tente outro arquivo ou imagem.")
    finally:
        os.remove(caminho) 


@api.post("/finalizar")
def finalizar(linha: Linha):
    try:
        destino = gravar(linha)
    except ErroDeGravacao as e:
        raise HTTPException(502, str(e))
    return {"ok": True, "destino": destino}

URL_VALIDA = re.compile(r"^https://script\.google\.com/(?:a/)?macros/(?:[^/]+/)?s/[A-Za-z0-9_-]+/exec$")


class ConfigEntrada(BaseModel):
    apps_script_url: str = ""
    apps_script_token: str | None = None


def _config_atual() -> dict:
    url, token = config.apps_script()
    return {
        "apps_script_url": url,
        "tem_token": bool(token),  
        "pasta_dados": str(config.pasta_dados()),
        "destino": "sheets" if url else "csv",
        "url_vem_do_ambiente": bool(os.getenv("APPS_SCRIPT_URL")),
    }


def _validar_url(url: str) -> None:
    if url and not URL_VALIDA.match(url):
        raise HTTPException(
            400,
            "Este endereço não parece ser de um app da web do Apps Script "
            "(deve começar com https://script.google.com/ e terminar em /exec).",
        )


@api.get("/config")
def ler_config():
    return _config_atual()


@api.put("/config")
def salvar_config(entrada: ConfigEntrada):
    url = entrada.apps_script_url.strip()
    _validar_url(url)
    novos = {"apps_script_url": url}
    if entrada.apps_script_token is not None:
        novos["apps_script_token"] = entrada.apps_script_token.strip()
    if not url:
        novos["apps_script_token"] = "" 
    try:
        config.salvar(novos)
    except OSError as e:
        raise HTTPException(500, f"Não consegui salvar as configurações: {e.strerror or e}")
    return _config_atual()


@api.post("/config/testar")
def testar_config(entrada: ConfigEntrada):
    url = entrada.apps_script_url.strip()
    if not url:
        raise HTTPException(400, "Cole primeiro o endereço do app da web.")
    _validar_url(url)
    token = entrada.apps_script_token if entrada.apps_script_token is not None else config.apps_script()[1]
    try:
        nome = testar_conexao(url, token.strip())
    except ErroDeGravacao as e:
        raise HTTPException(502, str(e))
    return {"ok": True, "planilha": nome}


@api.post("/abrir-pasta")
def abrir_pasta():
    pasta = config.pasta_dados()
    pasta.mkdir(parents=True, exist_ok=True)
    try:
        if sys.platform.startswith("win"):
            os.startfile(pasta)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(pasta)])
        else:
            subprocess.Popen(["xdg-open", str(pasta)])
    except Exception:
        raise HTTPException(500, f"Não consegui abrir a pasta. Ela fica em: {pasta}")
    return {"ok": True}

@api.get("/diagnostico")
def diagnostico_ocr():
    return diagnostico()

app.include_router(api)

def localizar_site() -> Path | None:
    candidatos = [
        os.getenv("STATIC_DIR"),
        BASE / "static",                                               
        Path(__file__).resolve().parent.parent / "frontend" / "out", 
    ]
    for c in candidatos:
        if c and (Path(c) / "index.html").exists():
            return Path(c)
    return None


_site = localizar_site()
if _site:
    app.mount("/", StaticFiles(directory=_site, html=True), name="site")
else:
    log.warning("Pasta do site não encontrada (rode 'npm run build' em frontend/). Só a API está ativa.")