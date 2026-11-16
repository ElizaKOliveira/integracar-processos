import json
import os
import tempfile
from pathlib import Path

from platformdirs import user_config_dir, user_documents_dir

NOME_APP = "LeitorProcessos"
_CHAVES = {"apps_script_url", "apps_script_token", "pasta_dados"}


def pasta_config() -> Path:
    # Windows: C:\Users\<nome>\AppData\Local\LeitorProcessos
    # Linux:   ~/.config/LeitorProcessos
    return Path(os.getenv("CONFIG_DIR") or user_config_dir(NOME_APP, appauthor=False))


def _arquivo() -> Path:
    return pasta_config() / "config.json"


def carregar() -> dict[str, str]:
    try:
        dados = json.loads(_arquivo().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(dados, dict):
        return {}
    return {k: v for k, v in dados.items() if k in _CHAVES and isinstance(v, str)}


def salvar(novos: dict[str, str]) -> None:
    atual = carregar()
    atual.update(novos)
    atual = {k: v for k, v in atual.items() if v}

    pasta = pasta_config()
    pasta.mkdir(parents=True, exist_ok=True)

    fd, caminho_tmp = tempfile.mkstemp(dir=pasta, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(atual, f, ensure_ascii=False, indent=2)
        try:
            os.chmod(caminho_tmp, 0o600)
        except OSError:
            pass
        os.replace(caminho_tmp, _arquivo())
    except Exception:
        if os.path.exists(caminho_tmp):
            os.remove(caminho_tmp)
        raise


def pasta_dados() -> Path:
    escolhida = os.getenv("DADOS_DIR") or carregar().get("pasta_dados")
    if escolhida:
        return Path(escolhida)
    return Path(user_documents_dir()) / "Leitor de Processos"


def apps_script() -> tuple[str, str]:
    cfg = carregar()
    url = (os.getenv("APPS_SCRIPT_URL") or cfg.get("apps_script_url") or "").strip()
    token = (os.getenv("APPS_SCRIPT_TOKEN") or cfg.get("apps_script_token") or "").strip()
    return url, token