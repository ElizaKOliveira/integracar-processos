export type Campos = {
  nome_arquivo: string;
  processo_nome: string;
  processo_simlam: string;
  interessado: string;
  cpf: string;
  data: string;
  origem: string;
  qnt_folhas: string;
  processo_edocs: string;
  registro: string;
};

export const CAMPOS_VAZIOS: Campos = {
  nome_arquivo: "",
  processo_nome: "",
  processo_simlam: "",
  interessado: "",
  cpf: "",
  data: "",
  origem: "",
  qnt_folhas: "",
  processo_edocs: "",
  registro: "",
};