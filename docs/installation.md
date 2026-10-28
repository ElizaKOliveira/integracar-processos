# Leitor de capas de processo (Simlam / CAR)

Sistema para ler a **capa** de processos ambientais, mostrar os dados
para você conferir e gravar o resultado em uma planilha.

**Como funciona:**

1.  Você arrasta a capa do processo (PDF ou imagem) para a tela.
2.  O sistema lê o texto da capa (OCR) **dentro do seu próprio
    computador**.
3.  Você confere os campos, corrige o que for preciso e preenche os
    campos manuais.
4.  Ao clicar em **Finalizado**, a linha é gravada e a tela é limpa para
    o próximo documento.

> **Privacidade:** o documento **não é enviado para a internet**. A
> leitura acontece só no seu computador. Os dados ficam em um arquivo
> local (`dados\processos.csv`) ou, se você configurar, na sua planilha
> do Google (veja a seção "Opcional").

------------------------------------------------------------------------

## Índice

-   [1. O que você vai precisar](#1-o-que-você-vai-precisar)
-   [2. Instalação no Windows](#2-instalação-no-windows)
    -   [2.1 Instalar o Docker Desktop](#21-instalar-o-docker-desktop)
    -   [2.2 Baixar o sistema](#22-baixar-o-sistema)
-   [3. Usar o sistema no Windows](#3-usar-o-sistema-no-windows)
    -   [3.1 Ligar (a primeira vez)](#31-ligar-a-primeira-vez)
    -   [3.2 Processar um documento](#32-processar-um-documento)
    -   [3.3 Onde ficam os resultados](#33-onde-ficam-os-resultados)
    -   [3.4 Desligar e ligar outras
        vezes](#34-desligar-e-ligar-outras-vezes)
    -   [3.5 Atualizar para uma versão
        nova](#35-atualizar-para-uma-versão-nova)
-   [4. Usando no Linux](#4-usando-no-linux)
    -   [4.1 Instalar o Docker (só uma
        vez)](#41-instalar-o-docker-só-uma-vez)
    -   [4.2 Baixar o sistema](#42-baixar-o-sistema)
    -   [4.3 Ligar](#43-ligar)
    -   [4.4 Resultados](#44-resultados)
    -   [4.5 Atualizar](#45-atualizar)
    -   [4.6 Problemas comuns no Linux](#46-problemas-comuns-no-linux)
    -   [4.7 Sem Docker (opcional, para quem
        prefere)](#47-sem-docker-opcional-para-quem-prefere)
-   [5. Opcional: gravar no Google
    Sheets](#5-opcional-gravar-no-google-sheets)
-   [6. Cuidados com os dados](#6-cuidados-com-os-dados)
-   [7. Problemas comuns no Windows](#7-problemas-comuns-no-windows)

------------------------------------------------------------------------

## 1. O que você vai precisar

-   Windows 10 ou 11 (64 bits)
-   No mínimo 8 GB de memória (RAM)
-   Conexão com a internet **apenas na instalação** (e para a planilha
    do Google, se usar)
-   Cerca de 3 GB livres no disco

------------------------------------------------------------------------

## 2. Instalação no Windows

### 2.1 Instalar o Docker Desktop

O Docker é o programa que "empacota" o sistema, para que você não
precise instalar nada mais.

1.  Acesse **https://www.docker.com/products/docker-desktop/** e baixe o
    **Docker Desktop para Windows**.
2.  Execute o instalador. Se aparecer a opção **"Use WSL 2"**, deixe
    marcada.
3.  Ao terminar, **reinicie o computador** se o instalador pedir.
4.  Abra o **Docker Desktop** pelo menu Iniciar, aceite os termos e
    aguarde até aparecer que ele está em execução (um indicador verde no
    canto inferior).

Se o Docker reclamar de **virtualização** ou **WSL**, veja a seção
"Problemas comuns" no final.

### 2.2 Baixar o sistema

1.  Receba o link do projeto (ou o arquivo `.zip`) de quem o
    desenvolveu.
2.  Se for pelo GitHub: clique no botão verde **Code → Download ZIP**.
3.  Extraia o ZIP em uma pasta simples, por exemplo
    `C:\leitor-processos`. Evite pastas dentro de "Downloads" ou com
    acentos no nome.

Dentro da pasta você deve ver, entre outros, os itens `backend`,
`frontend` e `docker-compose.yml`.

------------------------------------------------------------------------

## 3. Usar o sistema no Windows

### 3.1 Ligar (a primeira vez)

1.  Abra a pasta do projeto no Explorador de Arquivos.

2.  Clique na **barra de endereço** (onde aparece o caminho da pasta),
    apague o texto, digite `cmd` e aperte **Enter**. Abre uma janela
    preta (terminal) já dentro da pasta.

3.  Digite o comando abaixo e aperte Enter:

        docker compose up --build

4.  **Aguarde.** Na primeira vez demora vários minutos, porque o Docker
    baixa e monta tudo. Quando as mensagens pararem de correr e aparecer
    algo como "Ready" ou "Uvicorn running", está pronto.

5.  Abra o navegador (Chrome, Edge ou Firefox) e acesse:

    **http://127.0.0.1:3000**

    Use exatamente esse endereço (com os números). Se usar `localhost`,
    o sistema pode não funcionar.

### 3.2 Processar um documento

1.  **Arraste a capa** (PDF, PNG ou JPG) para a área indicada, ou clique
    para escolher. Pode ser um PDF grande: só a primeira página é lida.
2.  Aguarde a mensagem "Lendo..." (alguns segundos).
3.  À esquerda aparece a imagem da capa (para PDF, confira no arquivo
    original). À direita, os campos.
4.  **Confira cada campo** com o documento. Os campos em **amarelo**
    estão vazios: o sistema não conseguiu ler, e você precisa digitar.
5.  Preencha os campos manuais: **Qnt folhas**, **Processo E-DOCS** e
    **Num. Registro**.
6.  Clique em **Finalizado**. A tela é limpa e você pode enviar o
    próximo.

O botão **Finalizado** só fica ativo quando todos os campos estão
preenchidos. Se você errou de arquivo, use **"Descartar e escolher outro
arquivo"**.

### 3.3 Onde ficam os resultados

Na pasta do projeto, em **`dados\processos.csv`**. Cada documento vira
uma linha, e a última coluna (**Status**) começa como **"Falta
imprimir"**.

-   Abra o arquivo com o Excel (duplo clique).
-   **Feche o Excel antes de clicar em "Finalizado".** Se o arquivo
    estiver aberto, o Windows impede a gravação e o sistema avisa com um
    erro. Basta fechar e clicar de novo.
-   Faça cópia de segurança desse arquivo de vez em quando.

### 3.4 Desligar e ligar outras vezes

-   **Para desligar:** no terminal, aperte `Ctrl + C`. Se você usou o
    modo "em segundo plano" (abaixo), digite `docker compose down`.

-   **Nos próximos dias**, não precisa reconstruir nada. Abra o Docker
    Desktop, abra o terminal na pasta (passo 3.1.2) e digite:

        docker compose up -d

    O `-d` deixa o sistema rodando em segundo plano (pode fechar a
    janela preta). Espere uns 20 segundos e acesse
    http://127.0.0.1:3000.

### 3.5 Atualizar para uma versão nova

1.  Baixe o novo ZIP e extraia por cima da pasta antiga, **sem apagar**
    a pasta `dados` (seus resultados) nem o arquivo `.env`, se existir.
2.  No terminal, dentro da pasta: `docker compose up -d --build`

------------------------------------------------------------------------

## 4. Usando no Linux

Os passos das seções 2 e 3 são para Windows. No Linux é parecido, e mais
simples, porque o Docker roda direto no sistema (sem WSL). Os comandos
abaixo valem para Ubuntu e Debian; para outras distribuições, veja o
guia oficial em **https://docs.docker.com/engine/install/**.

### 4.1 Instalar o Docker (só uma vez)

``` bash
sudo apt update
sudo apt install docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Depois do último comando, **saia da sessão e entre de novo** (ou
reinicie), para você poder usar o Docker sem `sudo`. Confira:

``` bash
docker --version
docker compose version
```

> O grupo `docker` dá, na prática, poderes de administrador no
> computador. Em máquinas compartilhadas, prefira usar `sudo docker ...`
> em vez de entrar no grupo.

### 4.2 Baixar o sistema

Com Git:

``` bash
git clone <https://github.com/ElizaKOliveira/integracar-processos> leitor-processos
cd leitor-processos
```

Ou baixe o ZIP, extraia e entre na pasta pelo terminal.

### 4.3 Ligar

``` bash
mkdir -p dados
docker compose up --build
```

A primeira vez demora alguns minutos. Quando as mensagens pararem, abra
o navegador em **http://127.0.0.1:3000** (use exatamente esse endereço,
não `localhost`).

Nos outros dias: `docker compose up -d` (em segundo plano). Para
desligar: `docker compose down`.

### 4.4 Resultados

O arquivo fica em **`dados/processos.csv`**. O Docker o cria como
usuário *root*, então, para poder editar ou apagar, rode uma vez:

``` bash
sudo chown -R $USER dados
```

Para abrir no **LibreOffice Calc**: *Arquivo → Abrir*, escolha o CSV e,
na janela de importação, confira a codificação **UTF-8** e o separador
**ponto e vírgula (;)**. Feche o arquivo antes de clicar em
"Finalizado"; no Linux o sistema consegue gravar mesmo com ele aberto,
mas o LibreOffice não mostra as linhas novas e pode sobrescrevê-las se
você salvar.

### 4.5 Atualizar

``` bash
git pull
docker compose up -d --build
```

(ou extraia o novo ZIP por cima, sem apagar a pasta `dados` nem o
arquivo `.env`).

### 4.6 Problemas comuns no Linux

-   **`permission denied ... /var/run/docker.sock`:** você ainda não
    saiu e entrou na sessão depois do `usermod`, ou não está no grupo
    `docker`. Use `sudo docker compose ...` como solução rápida.
-   **`Cannot connect to the Docker daemon`:**
    `sudo systemctl start docker`.
-   **`port is already allocated`:** algo usa as portas 3000 ou 8000.
    Descubra com `ss -ltnp | grep -E ':3000|:8000'`.
-   **Fedora, RHEL ou outras com SELinux:** se o sistema não consegue
    gravar o CSV, no `docker-compose.yml` troque a linha do volume por
    `- ./dados:/app/dados:z`.
-   **O arquivo `.env` (para o Google Sheets):** crie na raiz do projeto
    com `nano .env` e as duas linhas descritas na seção 5. Cuidado para
    não deixá-lo visível a outras pessoas: `chmod 600 .env`.

### 4.7 Sem Docker (opcional, para quem prefere)

Exige Tesseract com o idioma português, Python 3.12+ e Node 20+.

``` bash
sudo apt install tesseract-ocr tesseract-ocr-por python3-venv nodejs npm

# Terminal 1: leitor (Python)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ALLOWED_ORIGIN=http://127.0.0.1:3000 uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 2: interface (Next.js)
cd frontend
npm ci
npm run dev -- -H 127.0.0.1
```

Nesse modo o CSV fica em `frontend/dados/processos.csv`, e as variáveis
do Google Sheets (se usar) vão em `frontend/.env.local`.

------------------------------------------------------------------------

## 5. Opcional: gravar no Google Sheets

Por padrão, tudo vai para o arquivo CSV, e **nenhuma configuração é
necessária**. Se você prefere uma planilha do Google, são necessários
uma planilha sua e um pequeno script (Apps Script) publicado por você.
No final você terá dois valores: um **URL** e um **token**. O token é
como uma senha: **não compartilhe nem publique**.

1.  Na pasta do projeto, crie um arquivo chamado `.env` (veja o aviso
    abaixo) com este conteúdo:

        APPS_SCRIPT_URL=cole_aqui_o_url_terminado_em_/exec
        APPS_SCRIPT_TOKEN=cole_aqui_o_token

2.  Reinicie o sistema: `docker compose down` e depois
    `docker compose up -d`.

Com os dois valores preenchidos, o sistema grava na planilha em vez do
CSV. Para apagar a configuração e voltar ao CSV, basta apagar essas duas
linhas.

> **Como criar o arquivo `.env` no Windows:** abra o Bloco de Notas,
> cole o conteúdo, vá em **Arquivo → Salvar como**, digite o nome
> **entre aspas**, `".env"`, escolha o tipo **"Todos os arquivos"** e
> salve na pasta do projeto. Sem as aspas, o Windows salva como
> `.env.txt` e não funciona.

O passo a passo para criar o script e o token está em
`apps-script/Codigo.gs` (o código) e deve ser configurado por quem for
administrar a planilha.

------------------------------------------------------------------------

## 6. Cuidados com os dados

-   **Nunca** envie a pasta `dados`, o arquivo `.env` ou documentos
    reais para o GitHub.
-   O sistema só é acessível no próprio computador (endereço
    `127.0.0.1`). Outras pessoas na mesma rede não conseguem abri-lo.
-   Se perder o computador ou o token vazar, troque o token no Apps
    Script (propriedade `TOKEN`) e atualize o `.env`.

------------------------------------------------------------------------

## 7. Problemas comuns no Windows

**O Docker Desktop não abre ou fala em "virtualização" / "WSL".**

A virtualização precisa estar ativada na BIOS do computador (procure por
"Virtualization", "VT-x" ou "SVM"). Para o WSL, abra o PowerShell como
administrador e rode `wsl --install`, depois reinicie.

**`docker` não é reconhecido como comando.**

Abra o Docker Desktop primeiro, espere ele iniciar por completo e abra
um terminal novo.

**A página http://127.0.0.1:3000 não abre.**

Confirme que o Docker Desktop está rodando e que o sistema foi ligado
(passo 3.1 ou 3.4). Confira também se você digitou `127.0.0.1`, e não
`localhost`. Dê uma olhada nos registros com `docker compose logs`.

**Aparece "Não consegui falar com o leitor (Python)".**

O serviço de leitura ainda está iniciando (espere 20 a 30 segundos e
recarregue a página) ou parou. Rode `docker compose up -d` de novo.

**O campo "Interessado", o CPF ou outro campo vem vazio ou errado.**

É normal em documentos com baixa qualidade: o OCR lê o que consegue. Por
isso existe a revisão. Digite o valor correto e siga. Se acontecer com
muitos documentos parecidos, avise quem mantém o sistema, enviando um
exemplo **com dados fictícios**, para ajustar a leitura.

**Erro ao clicar em "Finalizado" ("Não consegui gravar o arquivo").**

O `processos.csv` provavelmente está aberto no Excel. Feche o Excel e
clique em Finalizado de novo.

**Os acentos aparecem quebrados no Excel (por exemplo "Ã§").**

Em vez de dar duplo clique, no Excel use **Dados → De Texto/CSV**,
escolha o arquivo e selecione a codificação **UTF-8**.

**Dá erro de "porta em uso" (port is already allocated).**

Outro programa está usando as portas 3000 ou 8000. Feche-o ou reinicie o
computador.

**O computador ficou lento.**

O Docker Desktop consome memória enquanto está aberto. Quando terminar o
trabalho, rode `docker compose down` e feche o Docker Desktop.
