import { CAMPOS_VAZIOS, type Campos } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function extrairCampos(arquivo: File): Promise<Campos> {
  const corpo = new FormData();
  corpo.append("arquivo", arquivo);

  let resposta: Response;
  try {
    resposta = await fetch(`${API_URL}/extract`, { method: "POST", body: corpo });
  } catch {
    throw new Error(
      "Não consegui falar com o leitor (Python). Ele está rodando na porta 8000?"
    );
  }

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(erro?.detail ?? `Erro ${resposta.status} ao ler o documento.`);
  }

  const dados = await resposta.json();
  return { ...CAMPOS_VAZIOS, ...dados.campos } as Campos;
}

export async function enviarParaPlanilha(campos: Campos): Promise<void> {
  const resposta = await fetch("/api/finalizar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(campos),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(erro?.erro ?? "Falha ao enviar para a planilha.");
  }
}