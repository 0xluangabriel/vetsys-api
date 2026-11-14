export type Perfil = "comum" | "funcionario" | "admin" | "tutor";
export type Papel = "equipe" | "tutor";

export const TIPOS = ["Vacinação", "Castração", "Exame", "Consulta", "Cirurgia"] as const;
export type TipoProcedimento = (typeof TIPOS)[number];

export const FORMAS_PAGAMENTO = ["Cartão de Crédito", "Cartão de Débito", "Pix", "Dinheiro"] as const;
export type FormaPagamento = (typeof FORMAS_PAGAMENTO)[number];

export interface Tutor {
  id: number;
  nome: string;
  email: string;
  telefone: string;
  endereco: string | null;
  numero: string | null;
  complemento: string | null;
  cep: string | null;
}

export interface Animal {
  id: number;
  id_tutor: number;
  nome: string;
  especie: string;
  raca: string;
  sexo: string;
  idade: string;
  peso: number;
}

export interface Procedimento {
  id: number;
  id_animal: number;
  nome: string;
  descricao: string;
  preco: number | null;
  tipo: TipoProcedimento;
  forma_pagamento: FormaPagamento | null;
  /** Data no formato ISO: aaaa-mm-dd. */
  data: string;
}

export interface UsuarioAdmin {
  id: number;
  nome: string;
  email: string;
  perfil?: Perfil;
}

export interface TokenResposta {
  access_token: string;
  token_type: string;
}
