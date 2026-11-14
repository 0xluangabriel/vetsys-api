import type { Papel } from "./types.js";

interface Estado {
  token: string | null;
  email: string;
  papel: Papel;
  admin: boolean;
  /** Chave da tela aberta. */
  view: string;
  /** Página atual de cada tela com tabela. */
  pagina: Record<string, number>;
}

export const estado: Estado = {
  token: null,
  email: "",
  papel: "equipe",
  admin: false,
  view: "",
  pagina: {},
};

export function paginaAtual(view: string = estado.view): number {
  return estado.pagina[view] ?? 0;
}

export function guardar(chave: string, valor: string | null): void {
  try {
    if (valor === null) sessionStorage.removeItem(chave);
    else sessionStorage.setItem(chave, valor);
  } catch {
    /* navegador sem armazenamento: a sessão dura até fechar a aba */
  }
}

export function lerGuardado(chave: string): string | null {
  try {
    return sessionStorage.getItem(chave);
  } catch {
    return null;
  }
}
