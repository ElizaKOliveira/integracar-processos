"use client";

import { useState } from "react";
import {
  abrirPasta, lerConfig, salvarConfig, testarConfig, type ConfigServidor,
} from "@/lib/api";

type Aviso = { tipo: "ok" | "erro"; texto: string } | null;

export default function Configuracoes() {
  const [aberto, setAberto] = useState(false);
  const [cfg, setCfg] = useState<ConfigServidor | null>(null);
  const [url, setUrl] = useState("");
  const [token, setToken] = useState("");
  const [tokenTocado, setTokenTocado] = useState(false);
  const [aviso, setAviso] = useState<Aviso>(null);
  const [ocupado, setOcupado] = useState(false);

  async function abrir() {
    setAviso(null);
    setToken("");
    setTokenTocado(false);
    setAberto(true);
    try {
      const atual = await lerConfig();
      setCfg(atual);
      setUrl(atual.apps_script_url);
    } catch (e) {
      setAviso({ tipo: "erro", texto: e instanceof Error ? e.message : "Erro ao ler as configurações." });
    }
  }

  const entrada = () => ({
    apps_script_url: url.trim(),
    ...(tokenTocado ? { apps_script_token: token } : {}),
  });

  async function testar() {
    setOcupado(true);
    setAviso(null);
    try {
      const r = await testarConfig(entrada());
      setAviso({ tipo: "ok", texto: `Conectado${r.planilha ? ` à planilha "${r.planilha}"` : ""}.` });
    } catch (e) {
      setAviso({ tipo: "erro", texto: e instanceof Error ? e.message : "Falha no teste." });
    } finally {
      setOcupado(false);
    }
  }

  async function salvar() {
    setOcupado(true);
    setAviso(null);
    try {
      const novo = await salvarConfig(entrada());
      setCfg(novo);
      setToken("");
      setTokenTocado(false);
      setAviso({
        tipo: "ok",
        texto: novo.destino === "sheets"
          ? "Salvo. Os próximos documentos vão para o Google Sheets."
          : "Salvo. Os documentos serão gravados em CSV.",
      });
    } catch (e) {
      setAviso({ tipo: "erro", texto: e instanceof Error ? e.message : "Falha ao salvar." });
    } finally {
      setOcupado(false);
    }
  }

  async function abrirPastaDados() {
    try {
      await abrirPasta();
    } catch (e) {
      setAviso({ tipo: "erro", texto: e instanceof Error ? e.message : "Não consegui abrir a pasta." });
    }
  }

  const travado = cfg?.url_vem_do_ambiente ?? false;

  const campo =
    "mt-1 w-full rounded-lg border border-verde bg-bege px-3 py-2 text-sm text-verde outline-none " +
    "focus:ring-2 focus:ring-verde disabled:opacity-60";

  const botao =
    "rounded-lg border border-verde px-3 py-2 text-sm font-medium text-verde hover:bg-bege " +
    "disabled:opacity-50";

  return (
    <>
      <button
        onClick={abrir}
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-linha bg-bege-claro text-verde-medio transition hover:border-verde-suave hover:text-verde`}      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      </button>

      {aberto && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
          onClick={() => setAberto(false)}
        >
          <div
            className="w-full max-w-lg rounded-xl bg-bege p-6 text-verde shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-lg font-bold">Configurações</h2>

            <p className="mt-2 text-sm text-verde">
              Gravando em: <strong>{cfg?.destino === "sheets" ? "Google Sheets" : "arquivo CSV"}</strong>
            </p>

            <section className="mt-4">
              <p className="text-sm font-semibold">Arquivo CSV</p>
              <p className="mt-1 break-all text-xs text-verde">{cfg?.pasta_dados ?? "..."}</p>
              <button onClick={abrirPastaDados} className={`${botao} mt-2`}>
                Abrir pasta
              </button>
            </section>

            <section className="mt-5">
              <p className="text-sm font-semibold">Google Sheets (opcional)</p>
              <p className="mt-1 text-xs text-verde">
                Cole o endereço do app da web da sua planilha. Deixe vazio para gravar só em CSV.
              </p>

              {travado && (
                <p className="mt-2 rounded bg-bege p-2 text-xs text-verde">
                  O endereço foi definido pelo ambiente (arquivo .env ou Docker), então mudar aqui não tem efeito.
                </p>
              )}

              <label className="mt-3 block text-sm">
                Endereço do app da web
                <input
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={travado}
                  placeholder="https://script.google.com/macros/s/.../exec"
                  className={campo}
                />
              </label>

              <label className="mt-3 block text-sm">
                Token <span className="text-verde">(só se a sua planilha usa)</span>
                <input
                  type="password"
                  value={token}
                  disabled={travado}
                  autoComplete="off"
                  onChange={(e) => {
                    setToken(e.target.value);
                    setTokenTocado(true);
                  }}
                  placeholder={cfg?.tem_token ? "•••••••• (já salvo; apague para remover)" : "opcional"}
                  className={campo}
                />
              </label>

              <div className="mt-4 flex gap-2">
                <button
                  onClick={testar}
                  disabled={ocupado || !url.trim()}
                  className={botao}
                >
                  Testar conexão
                </button>

                <button
                  onClick={salvar}
                  disabled={ocupado || travado}
                  className="rounded-lg bg-verde px-3 py-2 text-sm font-semibold text-bege hover:opacity-80 disabled:opacity-50"
                >
                  Salvar
                </button>
              </div>
            </section>

            {aviso && (
              <p className={`mt-4 rounded-lg p-3 text-sm ${
                aviso.tipo === "ok"
                  ? "bg-bege text-verde"
                  : "bg-bege text-verde"
              }`}>
                {aviso.texto}
              </p>
            )}

            <div className="mt-5 text-right">
              <button onClick={() => setAberto(false)} className={botao}>
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
