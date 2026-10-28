"use client";
import { useRef, useState } from "react";

type Props = {
  aoEscolher: (arquivo: File) => void;
  desabilitado?: boolean;
};

const TIPOS_ACEITOS = ".pdf,.png,.jpg,.jpeg";

export default function UploadArea({ aoEscolher, desabilitado }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [arrastando, setArrastando] = useState(false);

  function receber(lista: FileList | null) {
    const arquivo = lista?.[0];
    if (arquivo) aoEscolher(arquivo);
  }

  return (
    <div
      onClick={() => !desabilitado && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault(); 
        setArrastando(true);
      }}
      onDragLeave={() => setArrastando(false)}
      onDrop={(e) => {
        e.preventDefault();
        setArrastando(false);
        if (!desabilitado) receber(e.dataTransfer.files);
      }}
      className={`group flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed px-6 py-20 text-center transition-all duration-200
        ${arrastando ? "border-verde bg-bege-escuro" : "border-linha bg-bege-claro hover:border-verde-suave hover:bg-bege-escuro/60"}
        ${desabilitado ? "pointer-events-none opacity-50" : ""}`}
    >
      <span
        className={`mb-6 flex h-14 w-14 items-center justify-center rounded-full border transition-colors
          ${arrastando ? "border-verde bg-verde text-bege" : "border-linha bg-bege text-verde group-hover:border-verde-suave"}`}
      >
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden
        >
          <path d="M12 16V4" />
          <path d="m7 9 5-5 5 5" />
          <path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />
        </svg>
      </span>

      <p className="font-serif text-2xl font-medium text-verde">
        Arraste a capa do processo aqui
      </p>
      <p className="mt-2 text-sm text-verde-suave">
        ou clique para escolher <span className="mx-1">·</span> PDF, PNG ou JPG
      </p>

      <input
        ref={inputRef}
        type="file"
        accept={TIPOS_ACEITOS}
        className="hidden"
        onChange={(e) => {
          receber(e.target.files);
          e.target.value = "";
        }}
      />
    </div>
  );
}