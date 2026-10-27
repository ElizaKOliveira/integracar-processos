import re


def _limpar(texto: str) -> str:
    return re.sub(r"[ \t]+", " ", texto)


def _buscar(padrao: str, texto: str, flags=re.IGNORECASE) -> str | None:
    achado = re.search(padrao, texto, flags=flags)
    return achado.group(1).strip() if achado else None


def extrair_campos(texto_bruto: str) -> dict:
    texto = _limpar(texto_bruto)

    achado = re.search(
        r"registrado\s+sob\s+n\S{0,2}\s*(\d{1,7})\s*[/\-]\s*(\d{4})",
        texto, flags=re.IGNORECASE,
    )
    numero, ano = (achado.group(1), achado.group(2)) if achado else (None, None)

    codigo = _buscar(r"\bc[óo]digo\s*:\s*(\w+)", texto)

    interessado = _buscar(r"interessado\s*:\s*(.+?)\s*[-–—]\s*CPF", texto)
    if not interessado:
        interessado = _buscar(r"interessado\s*:\s*([^\n]+)", texto)

    cpf = _buscar(
        r"(\d{3}\.\d{3}\.\d{3}-\d{2}|\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})", texto
    )

    origem = _buscar(
        r"local\s+e\s+data\s*:\s*([^\n,]+?)\s*[-–—]\s*[A-Z]{2}\s*,", texto
    )

    data = _buscar(
        r"local\s+e\s+data\s*:.*?(\d{2}[/.\-]\d{2}[/.\-]\d{4})",
        texto, flags=re.IGNORECASE | re.DOTALL,
    ) or _buscar(r"\b(\d{2}[/.\-]\d{2}[/.\-]\d{4})\b", texto)
    if data:
        data = re.sub(r"[.\-]", "/", data)  

    tem_tudo = numero and ano and codigo
    return {
        "nome_arquivo": f"Processo simlam {numero}-{ano} código do empreendimento nº {codigo}" if tem_tudo else "",
        "processo_nome": f"Processo técnico Simlam {numero}/{ano}, código do empreendimento nº {codigo}" if tem_tudo else "",
        "processo_simlam": f"{numero}/{ano}" if numero and ano else "",
        "interessado": interessado or "",
        "cpf": cpf or "",
        "data": data or "",
        "origem": origem or "",
        "qnt_folhas": "",
    }