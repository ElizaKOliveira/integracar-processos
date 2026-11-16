# Leitor de Capas de Processo

Aplicação web para automatizar a leitura de capas de processos ambientais, permitindo revisar os dados extraídos e exportá-los para uma planilha.

## Funcionalidades

- **Extração de texto (OCR):** leitura de capas de processos em PDF e imagens.
- **Revisão dos dados:** visualização e edição dos campos extraídos antes de salvar.
- **Exportação de dados:** armazenamento local em CSV.
- **Integração com Google Sheets:** opção de registrar os resultados diretamente em uma planilha.
- **Execução local:** processamento dos documentos no próprio computador.

## Tecnologias

- **Frontend:** Next.js (export estático), TypeScript e Tailwind CSS
- **Backend:** Python e FastAPI
- **OCR e PDF:** Tesseract OCR e PDFium (`pypdfium2`)
- **Empacotamento e CI/CD:** PyInstaller, Inno Setup e GitHub Actions
- **Infraestrutura e Integração:** Docker, Docker Compose e Google Apps Script

# Instalar e usar

| Sistema | Como |
|---|---|
| **Windows 10/11** | Baixe o instalador em [Releases](../../releases/latest) e siga o guia de instalação no site do projeto: https://leitorprocessos.vercel.app/ |
| **Linux** | Roda com Docker: `git clone`, depois `docker compose up -d --build` e abra <http://127.0.0.1:3000>. Passo a passo no mesmo guia (aba Linux). |

O instalador do Windows instala só para o usuário (não pede administrador), cria um atalho e **não apaga os dados** ao atualizar ou desinstalar.

## Privacidade

- O documento é lido localmente e o arquivo temporário é apagado logo após a leitura.
- O servidor escuta **apenas em `127.0.0.1`** e rejeita requisições de outros endereços (`Host`) ou de outros sites (`Origin`).
- Por padrão, nada sai do computador. Só se o usuário configurar o Google Sheets, a linha final de cada processo é enviada à planilha **dele**.
- Não versione capas reais, CSVs nem arquivos `.env` (já estão no `.gitignore`).

## Configuração

Valores podem vir de variáveis de ambiente (Docker e desenvolvimento) ou da tela **Configurações** do programa. A ordem de prioridade é: **variável de ambiente > `config.json` > padrão**.

| Variável | Para quê | Padrão |
|---|---|---|
| `DADOS_DIR` | Pasta do `processos.csv` | Documentos/Leitor de Processos |
| `CONFIG_DIR` | Pasta do `config.json` e dos logs | `%LOCALAPPDATA%\LeitorProcessos` (Windows), `~/.config/LeitorProcessos` (Linux) |
| `APPS_SCRIPT_URL` | Endereço (`/exec`) do app da web do Apps Script. Vazio = grava em CSV | vazio |
| `APPS_SCRIPT_TOKEN` | Token opcional do Apps Script | vazio |
| `TESSERACT_CMD` | Caminho do Tesseract (se não usar o embutido ou o do sistema) | automático |
| `STATIC_DIR` | Pasta do site (`index.html`) | automático |
| `ALLOWED_ORIGIN` | Libera CORS para o `next dev` (só desenvolvimento) | vazio |
| `NEXT_PUBLIC_API_URL` | Endereço da API **na hora de construir o site**. Em produção, deixe vazio | vazio |

A ordem de busca do Tesseract é: `TESSERACT_CMD` → pasta embutida `vendor/tesseract` → instalado no sistema (PATH).

## Google Sheets (opcional)

Cada usuário usa uma cópia da planilha modelo, que já contém o script. O código está em [`apps-script/Codigo.gs`](apps-script/Codigo.gs). Ele grava na primeira aba, tem o comando de teste de conexão (`ping`) e o token é opcional. O passo a passo para o usuário está no guia de instalação.

Cabeçalho esperado na linha 1 (colunas A a K): `Nome do arquivo`, `Processo nome`, `Processo Simlam`, `Interessado`, `CPF`, `Data`, `Origem`, `Qnt folhas`, `Processo E-DOCS`, `Registro`, `Status`.

## Desenvolvimento

### Estrutura

```
backend/                 API em Python (FastAPI), OCR, launcher e receita do PyInstaller
  main.py                rotas /api/... e serve o site
  ocr.py                 PDF/imagem -> texto (pypdfium2 + Tesseract)
  extractor.py           texto -> campos (regex, calibrado para a capa do Simlam)
  armazenamento.py       grava em CSV ou no Google Sheets
  config.py, caminhos.py configurações e pastas
  launcher.py            sobe o servidor e abre o navegador
  leitor.spec            PyInstaller (modo onedir)
frontend/                Next.js (export estático), Tailwind, TypeScript
installer/               leitor.iss (Inno Setup), AVISOS.txt, icone.ico
scripts/                 preparar_tesseract.py, smoke_test.py
apps-script/             Codigo.gs
.github/workflows/       instalador.yml (gera e publica o instalador)
Dockerfile, docker-compose.yml
```

### Rodar do código-fonte (Linux/macOS)

Requer Python 3.12+, Node 20+ e o Tesseract com o idioma português (Ubuntu/Debian: `sudo apt install tesseract-ocr tesseract-ocr-por`; Fedora: `sudo dnf install tesseract tesseract-langpack-por`).

```bash
# 1) Construir o site (NEXT_PUBLIC_API_URL vazio = chamadas relativas)
cd frontend
npm ci
NEXT_PUBLIC_API_URL="" npm run build

# 2) Subir o servidor (abre o navegador sozinho)
cd ../backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python launcher.py
```

### Desenvolver o front com recarregamento

```bash
# Terminal 1 (backend)
cd backend && source .venv/bin/activate
ALLOWED_ORIGIN=http://127.0.0.1:3000 uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 (frontend); crie frontend/.env.local com:
#   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
cd frontend && npm run dev -- -H 127.0.0.1
```

Antes de construir o site para produção, **não deixe** `NEXT_PUBLIC_API_URL` apontando para o backend de desenvolvimento (use o comando com a variável vazia, como acima).

### Docker

```bash
mkdir -p dados
docker compose up -d --build     # http://127.0.0.1:3000
```

Os dados ficam na pasta `dados/` (CSV em `dados/processos.csv`, configurações em `dados/config`).

### Gerar o instalador do Windows

O instalador é gerado pelo GitHub Actions (`.github/workflows/instalador.yml`), num Windows na nuvem: constrói o site, monta o Tesseract (`scripts/preparar_tesseract.py`), empacota com o PyInstaller, **liga o programa e confere a leitura de uma capa fictícia** (`scripts/smoke_test.py`) e compila o instalador com o Inno Setup.

- **Teste, sem publicar:** aba *Actions* → *Gerar instalador* → *Run workflow*. O arquivo sai como `Setup-LeitorDeProcessos-0.0.0-teste.exe`, em *Artifacts*. (*Re-run* reaproveita o commit antigo; para testar mudanças novas, use *Run workflow*.)
- **Versão oficial:** crie e envie uma tag que comece com `v`:

  ```bash
  git tag v1.0.0
  git push origin v1.0.0
  ```

  O workflow publica uma *release* com o instalador e o SHA-256 nas notas.

Para construir manualmente no Windows (PowerShell, com Python 3.12, Node 20+ e 7-Zip):

```powershell
$env:Path += ";C:\Program Files\7-Zip"
cd frontend; npm ci; $env:NEXT_PUBLIC_API_URL = ""; npm run build; cd ..
python scripts\preparar_tesseract.py
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt pyinstaller
.\.venv\Scripts\python -m PyInstaller leitor.spec --noconfirm
```

O resultado fica em `backend\dist\LeitorDeProcessos\`.

### Ajustar a leitura

A extração dos campos é calibrada para o layout da capa do Simlam e fica em `backend/extractor.py`. Para ajustar, rode o programa, envie uma capa **fictícia** e abra `/api/extract?debug=true` pelo Swagger (`/docs`) para ver o `texto_bruto` que o OCR produziu.

## Licenças de terceiros

O programa distribui, entre outros, Tesseract OCR (Apache-2.0), PDFium via pypdfium2 (BSD-3-Clause e Apache-2.0), FastAPI/Starlette/Uvicorn (MIT/BSD), Pillow (HPND) e Next.js/React (MIT). O resumo, incluído no instalador, está em [`installer/AVISOS.txt`](installer/AVISOS.txt).
