# Leitor de Capas de Processo — Simlam/CAR

Aplicação web para automatizar a leitura de capas de processos ambientais, permitindo revisar os dados extraídos e exportá-los para uma planilha.

## Funcionalidades

- **Extração de texto (OCR):** leitura de capas de processos em PDF e imagens.
- **Revisão dos dados:** visualização e edição dos campos extraídos antes de salvar.
- **Exportação de dados:** armazenamento local em CSV.
- **Integração com Google Sheets:** opção de registrar os resultados diretamente em uma planilha.
- **Execução local:** processamento dos documentos no próprio computador.

## Tecnologias

- **Frontend:** Next.js e TypeScript.
- **Backend:** Python e FastAPI.
- **OCR:** Tesseract.
- **Infraestrutura:** Docker e Docker Compose.
- **Integração opcional:** Google Apps Script e Google Sheets.

## Documentação

Consulte o manual para obter instruções de instalação e utilização:

**[📖 Manual de instalação e uso](docs/installation.md)**

O manual contém instruções específicas para Windows e Linux, além de orientações para atualização e solução de problemas.

## Privacidade

O processamento OCR ocorre localmente. Na configuração padrão, os resultados são armazenados em um arquivo CSV. A integração com o Google Sheets é opcional.