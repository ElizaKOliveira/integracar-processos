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
    <div className="space-y-5">
      <h2 className="font-serif text-xl font-medium text-verde">Revisão dos dados</h2>

      {DEFINICAO.map(({ chave, rotulo, dica }) => {
        const vazio = campos[chave].trim() === "";
        return (
          <label key={chave} className="block">
            <span className="flex items-baseline justify-between text-xs font-medium uppercase tracking-wider text-verde-medio">
              {rotulo}
              {dica && (
                <span className="ml-2 text-[11px] font-normal normal-case tracking-normal text-verde-suave">
                  {dica}
                </span>
              )}
            </span>
            <input
              type="text"
              value={campos[chave]}
              onChange={(e) => aoMudar({ ...campos, [chave]: e.target.value })}
              autoFocus={chave === "qnt_folhas"}
              inputMode={chave === "qnt_folhas" ? "numeric" : undefined}
              className={`mt-1.5 w-full rounded-lg border px-3.5 py-2.5 text-verde outline-none transition focus:ring-2
                ${
                  vazio
                    ? "border-alerta/60 bg-alerta-bg focus:border-alerta focus:ring-alerta/25"
                    : "border-linha bg-bege focus:border-verde-medio focus:ring-verde-medio/20"
                }`}
            />
            {vazio && (
              <span className="mt-1 block text-xs text-alerta">
                Vazio: confira o documento e preencha.
              </span>
            )}
          </label>
        );
      })}

      <button
        onClick={aoFinalizar}
        disabled={!podeFinalizar}
        className="w-full rounded-lg bg-verde px-4 py-3.5 text-sm font-medium uppercase tracking-[0.15em] text-bege transition
          hover:bg-verde-medio disabled:cursor-not-allowed disabled:bg-bege-escuro disabled:text-verde-suave"
      >
        {enviando ? "Enviando..." : "Finalizado"}
      </button>
    </div>
  );
}