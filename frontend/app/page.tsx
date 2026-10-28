"use client";
import { useState } from "react";
import UploadArea from "@/components/UploadArea";
import FormularioRevisao from "@/components/FormularioRevisao";
import ThemeToggle from "@/components/ThemeToggle";
import { extrairCampos, enviarParaPlanilha } from "@/lib/api";
import { CAMPOS_VAZIOS, type Campos } from "@/lib/types";

type Etapa = "aguardando" | "lendo" | "revisando";

export default function Home() {
  const [etapa, setEtapa] = useState<Etapa>("aguardando");
  const [campos, setCampos] = useState<Campos>(CAMPOS_VAZIOS);
  const [nomeOriginal, setNomeOriginal] = useState("");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [concluidos, setConcluidos] = useState(0);

  function limparTela() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setCampos(CAMPOS_VAZIOS);
    setNomeOriginal("");
    setEtapa("aguardando");
  }

  async function aoEscolherArquivo(arquivo: File) {
    setErro(null);
    setEtapa("lendo");
    setNomeOriginal(arquivo.name);
    setPreviewUrl(arquivo.type.startsWith("image/") ? URL.createObjectURL(arquivo) : null);
    try {
      setCampos(await extrairCampos(arquivo));
      setEtapa("revisando");
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Erro desconhecido.");
      limparTela();
    }
  }

  async function aoFinalizar() {
    setEnviando(true);
    setErro(null);
    try {
      await enviarParaPlanilha(campos);
      setConcluidos((n) => n + 1);
      limparTela();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Falha ao enviar para a planilha.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-12 sm:py-16">
      <header className="mb-10 flex flex-col gap-4 border-b border-linha pb-8 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-[0.25em] text-verde-suave">
            IntegraCAR
          </p>
          <h1 className="font-serif text-3xl font-medium tracking-tight text-verde sm:text-4xl">
            Leitor de capas de processo
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-full border border-linha bg-bege-claro px-4 py-1.5 text-sm text-verde-medio">
            <span className="h-1.5 w-1.5 rounded-full bg-verde-medio" />
            Concluídos nesta sessão
            <span className="font-serif text-base font-semibold text-verde">{concluidos}</span>
          </div>
          <ThemeToggle />
      </div>
      </header>

      {erro && (
        <div
          role="alert"
          className="mb-6 rounded-xl border border-erro/30 bg-erro-bg px-4 py-3 text-sm text-erro"
        >
          {erro}
        </div>
      )}

      {etapa === "aguardando" && <UploadArea aoEscolher={aoEscolherArquivo} />}

      {etapa === "lendo" && (
        <div className="flex flex-col items-center rounded-2xl border border-linha bg-bege-claro px-6 py-20 text-center">
          <span
            aria-hidden
            className="mb-6 h-9 w-9 animate-spin rounded-full border-2 border-linha border-t-verde"
          />
          <p className="text-verde-medio">
            Lendo <strong className="font-semibold text-verde">{nomeOriginal}</strong>...
          </p>
          <p className="mt-1 text-sm text-verde-suave">Isto pode levar alguns segundos.</p>
        </div>
      )}

      {etapa === "revisando" && (
        <div className="grid gap-6 md:grid-cols-2">
          <section className="self-start rounded-2xl border border-linha bg-bege-claro p-5 shadow-[0_1px_0_rgba(28,58,46,0.04)]">
            <p className="mb-3 truncate text-xs font-medium uppercase tracking-widest text-verde-suave">
              {nomeOriginal}
            </p>
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Capa enviada"
                className="w-full rounded-lg border border-linha"
              />
            ) : (
              <div className="rounded-lg border border-dashed border-linha bg-bege px-4 py-12 text-center text-sm text-verde-suave">
                Pré-visualização indisponível para PDF. Confira no arquivo original.
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-linha bg-bege-claro p-6 shadow-[0_1px_0_rgba(28,58,46,0.04)]">
            <FormularioRevisao
              campos={campos}
              aoMudar={setCampos}
              aoFinalizar={aoFinalizar}
              enviando={enviando}
            />
            <button
              onClick={limparTela}
              className="mt-4 w-full text-sm text-verde-suave underline-offset-4 transition hover:text-verde hover:underline"
            >
              Descartar e escolher outro arquivo
            </button>
          </section>
        </div>
      )}
    </main>
  );
}