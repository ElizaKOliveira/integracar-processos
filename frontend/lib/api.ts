import { CAMPOS_VAZIOS, type Campos } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

async function lerErro(resposta: Response, padrao: string): Promise<string> {
  const corpo = await resposta.json().catch(() => null);
  return typeof corpo?.detail === "string" ? corpo.detail : padrao;
}

export async function extrairCampos(arquivo: File): Promise<Campos> {
  const corpo = new FormData();
  corpo.append("arquivo", arquivo);

  let resposta: Response;
  try {
    resposta = await fetch(`${BASE}/api/extract`, { method: "POST", body: corpo });
  } catch {
    throw new Error("Não consegui falar com o leitor. O programa ainda está aberto?");
  }
  if (!resposta.ok) {
    throw new Error(await lerErro(resposta, `Erro ${resposta.status} ao ler o documento.`));
  }

  const dados = await resposta.json();
  return { ...CAMPOS_VAZIOS, ...dados.campos } as Campos;
}

export async function enviarParaPlanilha(campos: Campos): Promise<void> {
  let resposta: Response;
  try {
    resposta = await fetch(`${BASE}/api/finalizar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(campos),
    });
  } catch {
    throw new Error("Não consegui falar com o leitor. O programa ainda está aberto?");
  }
  if (!resposta.ok) {
    throw new Error(await lerErro(resposta, "Falha ao gravar."));
  }
}

export type ConfigServidor = {
  apps_script_url: string;
  tem_token: boolean;
  pasta_dados: string;
  destino: "csv" | "sheets";
  url_vem_do_ambiente: boolean;
};

async function chamar<T>(caminho: string, metodo: string, corpo?: unknown): Promise<T> {
  let resposta: Response;
  try {
    resposta = await fetch(`${BASE}${caminho}`, {
      method: metodo,
      headers: corpo !== undefined ? { "Content-Type": "application/json" } : undefined,
      body: corpo !== undefined ? JSON.stringify(corpo) : undefined,
    });
  } catch {
    throw new Error("Não consegui falar com o leitor. O programa ainda está aberto?");
  }
  if (!resposta.ok) throw new Error(await lerErro(resposta, `Erro ${resposta.status}.`));
  return resposta.json() as Promise<T>;
}


type Entrada = { apps_script_url: string; apps_script_token?: string };

export const lerConfig = () => chamar<ConfigServidor>("/api/config", "GET");
export const salvarConfig = (e: Entrada) => chamar<ConfigServidor>("/api/config", "PUT", e);
export const testarConfig = (e: Entrada) =>
  chamar<{ ok: boolean; planilha: string }>("/api/config/testar", "POST", e);
export const abrirPasta = () => chamar<{ ok: boolean }>("/api/abrir-pasta", "POST");