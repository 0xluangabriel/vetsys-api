import { api } from "./api.js";
import { CONFIG } from "./config.js";
import type { Animal, Procedimento, Tutor } from "./types.js";

/** Buscas de apoio: trazem até o máximo permitido, para preencher nomes e listas de seleção. */
const tudo = `skip=0&limit=${CONFIG.LIMITE_MAXIMO}`;

export const carregarTutores = (): Promise<Tutor[]> => api<Tutor[]>(`/tutores?${tudo}`);
export const carregarAnimais = (): Promise<Animal[]> => api<Animal[]>(`/animais?${tudo}`);
export const carregarProcedimentos = (): Promise<Procedimento[]> => api<Procedimento[]>(`/procedimentos?${tudo}`);

export function pagina(numero: number): string {
  return `skip=${numero * CONFIG.LIMITE}&limit=${CONFIG.LIMITE}`;
}

export function porId<T extends { id: number }>(lista: T[]): Map<number, T> {
  return new Map(lista.map((item) => [item.id, item]));
}
