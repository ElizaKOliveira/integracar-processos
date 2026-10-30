import { NextResponse } from "next/server";
import { appendFile, mkdir, access } from "node:fs/promises";
import path from "node:path";


const CHAVES = [
  "nome_arquivo", "processo_nome", "processo_simlam", "interessado", "cpf",
  "data", "origem", "qnt_folhas", "processo_edocs", "registro",
] as const;

const CABECALHOS = [
  "Nome do arquivo", "Processo nome", "Processo Simlam", "Interessado", "CPF",
  "Data", "Origem", "Qnt folhas", "Processo E-DOCS", "Registro Termo", "Status",
];
const STATUS_PADRAO = "Falta imprimir";


function celula(valor: string): string {
  let t = valor.replace(/\r?\n/g, " ");
  if (/^[=+\-@]/.test(t)) t = "'" + t;
  return `"${t.replace(/"/g, '""')}"`;
}

async function gravarCsv(campos: Record<string, string>) {
  const pasta = process.env.DADOS_DIR ?? path.join(process.cwd(), "dados");
  const arquivo = path.join(pasta, "processos.csv");
  await mkdir(pasta, { recursive: true });

  let existe = true;
  try { await access(arquivo); } catch { existe = false; }

  let texto = existe ? "" : "\uFEFF" + CABECALHOS.map(celula).join(";") + "\r\n";
  texto += [...CHAVES.map((k) => campos[k]), STATUS_PADRAO].map(celula).join(";") + "\r\n";

  await appendFile(arquivo, texto, "utf8");
}

async function enviarParaSheets(url: string, token: string, campos: Record<string, string>) {
  const resposta = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, campos }),
    redirect: "follow",
    signal: AbortSignal.timeout(20000),
  });
  const resultado = await resposta.json().catch(() => null);
  if (!resposta.ok || !resultado?.ok) {
    throw new Error(resultado?.erro ?? `Apps Script respondeu ${resposta.status}`);
  }
}

export async function POST(req: Request) {
  const corpo = await req.json().catch(() => null);
  if (!corpo || typeof corpo !== "object") {
    return NextResponse.json({ erro: "Corpo inválido." }, { status: 400 });
  }
  const campos: Record<string, string> = {};
  for (const chave of CHAVES) {
    const valor = (corpo as Record<string, unknown>)[chave];
    campos[chave] = typeof valor === "string" ? valor.trim() : "";
  }

  const url = process.env.APPS_SCRIPT_URL;
  const token = process.env.APPS_SCRIPT_TOKEN;

  try {
    if (url && token) {
      await enviarParaSheets(url, token, campos);
      return NextResponse.json({ ok: true, destino: "sheets" });
    }
    await gravarCsv(campos);
    return NextResponse.json({ ok: true, destino: "csv" });
  } catch (e) {
    const msg = url && token
      ? "Não consegui gravar na planilha (internet ou configuração)."
      : "Não consegui gravar o arquivo. Se o processos.csv estiver aberto no Excel, feche-o e tente de novo.";
    console.error(e);
    return NextResponse.json({ erro: msg }, { status: 502 });
  }
}