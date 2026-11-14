import { api } from "./api.js";
import { CONFIG } from "./config.js";
/** Buscas de apoio: trazem até o máximo permitido, para preencher nomes e listas de seleção. */
const tudo = `skip=0&limit=${CONFIG.LIMITE_MAXIMO}`;
export const carregarTutores = () => api(`/tutores?${tudo}`);
export const carregarAnimais = () => api(`/animais?${tudo}`);
export const carregarProcedimentos = () => api(`/procedimentos?${tudo}`);
export function pagina(numero) {
    return `skip=${numero * CONFIG.LIMITE}&limit=${CONFIG.LIMITE}`;
}
export function porId(lista) {
    return new Map(lista.map((item) => [item.id, item]));
}
