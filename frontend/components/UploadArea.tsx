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
        e.preventDefault(); // sem isto o navegador não aceita soltar o arquivo aqui
        setArrastando(true);
      }}
      onDragLeave={() => setArrastando(false)}
      onDrop={(e) => {
        e.preventDefault();
        setArrastando(false);
        if (!desabilitado) receber(e.dataTransfer.files);
      }}
      className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 text-center transition
        ${arrastando ? "border-emerald-500 bg-emerald-50" : "border-gray-300 bg-white hover:border-gray-400"}
        ${desabilitado ? "pointer-events-none opacity-50" : ""}`}
    >
      <p className="text-lg font-medium text-gray-700">
        Arraste a capa do processo aqui
      </p>
      <p className="mt-1 text-sm text-gray-500">
        ou clique para escolher (PDF, PNG ou JPG)
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