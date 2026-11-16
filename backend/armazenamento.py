import config
import csv
import os
import threading
from pathlib import Path

import httpx
from pydantic import BaseModel

CHAVES = [
    "nome_arquivo", "processo_nome", "processo_simlam", "interessado", "cpf",
    "data", "origem", "qnt_folhas", "processo_edocs", "registro",
]
CABECALHOS = [
    "Nome do arquivo", "Processo nome", "Processo Simlam", "Interessado", "CPF",
    "Data", "Origem", "Qnt folhas", "Processo E-DOCS", "Registro Termo", "Status",
]
STATUS_PADRAO = "Falta imprimir"


class Linha(BaseModel):
    nome_arquivo: str = ""
    processo_nome: str = ""
    processo_simlam: str = ""
    interessado: str = ""
    cpf: str = ""
    data: str = ""
    origem: str = ""
    qnt_folhas: str = ""
    processo_edocs: str = ""
    registro: str = ""


class ErroDeGravacao(Exception):
    """Mensagem de erro"""

_trava = threading.Lock()


def pasta_dados() -> Path:
    return Path(os.getenv("DADOS_DIR", "dados"))


def _celula(valor: str) -> str:
    texto = " ".join(valor.split())
    return "'" + texto if texto[:1] in ("=", "+", "-", "@") else texto


def _gravar_csv(dados: dict[str, str]) -> None:
    pasta = config.pasta_dados()
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / "processos.csv"

    try:
        with _trava:
            novo = not arquivo.exists()
            with open(arquivo, "a", encoding="utf-8", newline="") as f:
                if novo:
                    f.write("\ufeff") 
                escritor = csv.writer(f, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\r\n")
                if novo:
                    escritor.writerow(CABECALHOS)
                escritor.writerow([_celula(dados[k]) for k in CHAVES] + [STATUS_PADRAO])
    except PermissionError:
        raise ErroDeGravacao(
            "Não consegui gravar o arquivo. Se o processos.csv estiver aberto no Excel, "
            "feche-o e tente de novo."
        )
    except OSError as e:
        raise ErroDeGravacao(f"Não consegui gravar o arquivo: {e.strerror or e}")


def _chamar_script(url: str, carga: dict) -> dict:
    
    try:
        resposta = httpx.post(url, json=carga, follow_redirects=True, timeout=20)
    except httpx.HTTPError:
        raise ErroDeGravacao("Não consegui falar com a planilha (internet ou endereço incorreto).")

    try:
        resultado = resposta.json()
    except ValueError:
        resultado = None

    if resposta.status_code >= 400 or not isinstance(resultado, dict) or not resultado.get("ok"):
        motivo = resultado.get("erro") if isinstance(resultado, dict) else None
        raise ErroDeGravacao(
            f"A planilha recusou o envio: {motivo or 'resposta inesperada'}. "
            "Confira se o app da web foi publicado com acesso para 'Qualquer pessoa'."
        )
    return resultado


def testar_conexao(url: str, token: str) -> str:
    carga: dict = {"acao": "ping"}
    if token:
        carga["token"] = token
    resultado = _chamar_script(url, carga)
    return str(resultado.get("planilha", ""))


def gravar(linha: Linha) -> str:
    dados = {k: getattr(linha, k).strip() for k in CHAVES}
    url, token = config.apps_script()

    if url:
        carga: dict = {"campos": dados}
        if token:
            carga["token"] = token
        _chamar_script(url, carga)
        return "sheets"
    _gravar_csv(dados)
    return "csv"