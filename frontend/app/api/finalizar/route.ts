import { NextResponse } from "next/server";

const CHAVES = [
  "nome_arquivo", "processo_nome", "processo_simlam", "interessado", "cpf",
  "data", "origem", "qnt_folhas", "processo_edocs", "registro",
] as const;

export async function POST(req: Request) {
  const url = process.env.APPS_SCRIPT_URL;
  const token = process.env.APPS_SCRIPT_TOKEN;
  if (!url || !token) {
    return NextResponse.json(
      { erro: "Faltam APPS_SCRIPT_URL / APPS_SCRIPT_TOKEN no .env.local" },
      { status: 500 }
    );
  }

  const corpo = await req.json().catch(() => null);
  if (!corpo || typeof corpo !== "object") {
    return NextResponse.json({ erro: "Corpo inválido." }, { status: 400 });
  }

  const campos: Record<string, string> = {};
  for (const chave of CHAVES) {
    const valor = (corpo as Record<string, unknown>)[chave];
    campos[chave] = typeof valor === "string" ? valor.trim() : "";
  }

  try {
    const resposta = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, campos }),
      redirect: "follow",
      signal: AbortSignal.timeout(20000), // desiste após 20 s
    });

    const resultado = await resposta.json().catch(() => null);
    if (!resposta.ok || !resultado?.ok) {
      return NextResponse.json(
        { erro: resultado?.erro ?? `Apps Script respondeu ${resposta.status}` },
        { status: 502 }
      );
    }
    return NextResponse.json({ ok: true, linha: resultado.linha });
  } catch {
    return NextResponse.json(
      { erro: "Não consegui falar com a planilha (internet ou URL errada)." },
      { status: 502 }
    );
  }
}