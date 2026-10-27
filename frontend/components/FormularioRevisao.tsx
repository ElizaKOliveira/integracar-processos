// components/FormularioRevisao.tsx
"use client";

import type { Campos } from "@/lib/types";

type Props = {
  campos: Campos;
  aoMudar: (novos: Campos) => void;
  aoFinalizar: () => void;
  enviando: boolean;
};


const DEFINICAO: { chave: keyof Campos; rotulo: string; dica?: string }[] = [
  { chave: "nome_arquivo", rotulo: "Nome do arquivo" },
  { chave: "processo_nome", rotulo: "Processo nome" },
  { chave: "processo_simlam", rotulo: "Processo Simlam", dica: "número/ano" },
  { chave: "interessado", rotulo: "Interessado" },
  { chave: "cpf", rotulo: "CPF" },
  { chave: "data", rotulo: "Data", dica: "DD/MM/AAAA" },
  { chave: "origem", rotulo: "Origem", dica: "município" },
  { chave: "qnt_folhas", rotulo: "Qnt folhas", dica: "preencha manualmente" },
  { chave: "processo_edocs", rotulo: "Processo E-DOCS", dica: "preencha manualmente" },
  { chave: "registro", rotulo: "Registro Termo", dica: "preencha manualmente" },

];

export default function FormularioRevisao({ campos, aoMudar, aoFinalizar, enviando }: Props) {
  const vazios = DEFINICAO.filter((d) => campos[d.chave].trim() === "");
  const podeFinalizar = vazios.length === 0 && !enviando;

  return (
    <div className="space-y-4">
      {DEFINICAO.map(({ chave, rotulo, dica }) => {
        const vazio = campos[chave].trim() === "";
        return (
          <label key={chave} className="block">
            <span className="text-sm font-medium text-gray-700">
              {rotulo}
              {dica && <span className="ml-2 font-normal text-gray-400">{dica}</span>}
            </span>
            <input
              type="text"
              value={campos[chave]}
              onChange={(e) => aoMudar({ ...campos, [chave]: e.target.value })}
              autoFocus={chave === "qnt_folhas"}
              inputMode={chave === "qnt_folhas" ? "numeric" : undefined}
              className={`mt-1 w-full rounded-lg border px-3 py-2 outline-none focus:ring-2
                ${vazio ? "border-amber-400 bg-amber-50 focus:ring-amber-300" : "border-gray-300 bg-white focus:ring-emerald-300"}`}
            />
            {vazio && (
              <span className="text-xs text-amber-600">Vazio: confira o documento e preencha.</span>
            )}
          </label>
        );
      })}

      <button
        onClick={aoFinalizar}
        disabled={!podeFinalizar}
        className="w-full rounded-lg bg-emerald-600 px-4 py-3 font-semibold text-white transition
          hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-gray-300"
      >
        {enviando ? "Enviando..." : "Finalizado"}
      </button>
    </div>
  );
}