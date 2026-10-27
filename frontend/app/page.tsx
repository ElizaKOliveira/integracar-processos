"use client";

import { useState } from "react";
import UploadArea from "@/components/UploadArea";
import FormularioRevisao from "@/components/FormularioRevisao";
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
    <main className="mx-auto max-w-5xl p-6">
      <header className="mb-6 flex items-baseline justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Leitor de capas de processo</h1>
        <span className="text-sm text-gray-500">Concluídos nesta sessão: {concluidos}</span>
      </header>

      {erro && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {erro}
        </div>
      )}

      {etapa === "aguardando" && <UploadArea aoEscolher={aoEscolherArquivo} />}

      {etapa === "lendo" && (
        <div className="rounded-xl border bg-white p-12 text-center text-gray-600">
          Lendo <strong>{nomeOriginal}</strong>... isto pode levar alguns segundos.
        </div>
      )}

      {etapa === "revisando" && (
        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-xl border bg-white p-4">
            <p className="mb-2 truncate text-sm text-gray-500">{nomeOriginal}</p>
            {previewUrl ? (
              <img src={previewUrl} alt="Capa enviada" className="w-full rounded" />
            ) : (
              <p className="text-sm text-gray-400">
                Pré-visualização indisponível para PDF. Confira no arquivo original.
              </p>
            )}
          </section>

          <section className="rounded-xl border bg-white p-4">
            <FormularioRevisao
              campos={campos}
              aoMudar={setCampos}
              aoFinalizar={aoFinalizar}
              enviando={enviando}
            />
            <button
              onClick={limparTela}
              className="mt-3 w-full text-sm text-gray-500 underline hover:text-gray-700"
            >
              Descartar e escolher outro arquivo
            </button>
          </section>
        </div>
      )}
    </main>
  );
}