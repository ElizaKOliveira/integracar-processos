import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

PASTA_BACKEND = Path(SPECPATH)
SITE = PASTA_BACKEND.parent / "frontend" / "out"
TESSERACT = PASTA_BACKEND / "vendor" / "tesseract"

if not (SITE / "index.html").exists():
    raise SystemExit("Site não encontrado. Rode 'npm run build' em frontend/ antes (com NEXT_PUBLIC_API_URL vazio).")

datas = [(str(SITE), "static")]
if sys.platform == "win32":
    if not (TESSERACT / "tesseract.exe").exists():
        raise SystemExit("Tesseract não encontrado. Rode 'python scripts/preparar_tesseract.py' antes.")
    datas.append((str(TESSERACT), "vendor/tesseract"))

hiddenimports = collect_submodules("uvicorn") + collect_submodules("anyio")

a = Analysis(
    ["launcher.py"],
    pathex=[str(PASTA_BACKEND)],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "numpy"],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="LeitorDeProcessos",
    console=True,   
    upx=False,      
    icon=None,      
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="LeitorDeProcessos")