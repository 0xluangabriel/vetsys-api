import { PATA } from "./icones.js";
/* ===== Seleção de elementos ===== */
export function $(seletor, raiz = document) {
    const el = raiz.querySelector(seletor);
    if (!el)
        throw new Error(`Elemento não encontrado: ${seletor}`);
    return el;
}
export function $$(seletor, raiz = document) {
    return Array.from(raiz.querySelectorAll(seletor));
}
/** Escapa texto vindo da API antes de colocar no HTML (evita XSS). */
export function esc(valor) {
    const mapa = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
    return String(valor ?? "").replace(/[&<>"']/g, (c) => mapa[c] ?? c);
}
/* ===== Formatação ===== */
export const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
const moeda = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const numero = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });
export const brl = (valor) => moeda.format(valor);
export const kg = (valor) => `${numero.format(valor)} kg`;
const dois = (n) => String(n).padStart(2, "0");
export function dataISO(d = new Date()) {
    return `${d.getFullYear()}-${dois(d.getMonth() + 1)}-${dois(d.getDate())}`;
}
export function dataBR(iso) {
    if (!iso)
        return "—";
    const [ano, mes, dia] = iso.split("-");
    return `${dia}/${mes}/${ano}`;
}
/** Dia e mês abreviado de uma data ISO, para os blocos de agenda. */
export function diaMes(iso) {
    const [, mes = "01", dia = "01"] = iso.split("-");
    return { dia, mes: MESES[Number(mes) - 1] ?? "" };
}
export function fone(t) {
    const s = String(t ?? "");
    if (s.length === 11)
        return `(${s.slice(0, 2)}) ${s.slice(2, 7)}-${s.slice(7)}`;
    if (s.length === 10)
        return `(${s.slice(0, 2)}) ${s.slice(2, 6)}-${s.slice(6)}`;
    return s;
}
export function cep(c) {
    const s = String(c ?? "");
    return s.length === 8 ? `${s.slice(0, 5)}-${s.slice(5)}` : s;
}
export function sexo(s) {
    const mapa = { M: "Macho", F: "Fêmea" };
    return mapa[s.toUpperCase()] ?? s;
}
export function resumo(texto, limite = 70) {
    const t = String(texto ?? "");
    return t.length > limite ? `${t.slice(0, limite - 1)}…` : t;
}
/* ===== Avatares e etiquetas ===== */
export function iniciais(texto) {
    const partes = (texto || "?").split("@")[0].split(/[\s._-]+/).filter(Boolean);
    return ((partes[0]?.[0] ?? "?") + (partes[1]?.[0] ?? "")).toUpperCase();
}
export function corAvatar(texto) {
    let h = 0;
    for (const c of texto)
        h = (h * 31 + c.charCodeAt(0)) >>> 0;
    return `av-${h % 6}`;
}
export function avatar(texto, opcoes = {}) {
    const classes = ["avatar", corAvatar(texto), opcoes.redondo ? "redondo" : ""].join(" ").trim();
    return `<span class="${classes}" aria-hidden="true">${opcoes.pata ? PATA : esc(iniciais(texto))}</span>`;
}
function semAcento(t) {
    return t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}
export const classeTipo = (t) => `t-${semAcento(t)}`;
export function badgeTipo(t) {
    return `<span class="badge ${classeTipo(t)}">${esc(t)}</span>`;
}
export function badgePagamento(forma) {
    return forma
        ? `<span class="badge pg-pago">${esc(forma)}</span>`
        : `<span class="badge pg-pendente">Pendente</span>`;
}
const ROTULO_PERFIL = {
    admin: "Administrador",
    funcionario: "Funcionário",
    tutor: "Tutor",
    comum: "Sem acesso",
};
export function badgePerfil(perfil) {
    if (!perfil)
        return "—";
    return `<span class="badge p-${perfil}">${ROTULO_PERFIL[perfil]}</span>`;
}
/* ===== Avisos ===== */
export function toast(mensagem, erro = false) {
    const el = document.createElement("div");
    el.className = `toast${erro ? " erro" : ""}`;
    el.textContent = mensagem;
    $("#toasts").appendChild(el);
    const sair = () => {
        el.classList.add("saindo");
        el.addEventListener("animationend", () => el.remove(), { once: true });
        // Garante a remoção quando as animações estão desligadas.
        setTimeout(() => el.remove(), 400);
    };
    setTimeout(sair, erro ? 6000 : 3500);
}
/* ===== Animação ===== */
export const semMovimento = () => typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
/** Anima um número de 0 até o valor final. */
export function contarAte(el, alvo, sufixo = "") {
    if (semMovimento() || alvo === 0) {
        el.textContent = `${alvo}${sufixo}`;
        return;
    }
    const duracao = 700;
    const inicio = performance.now();
    const passo = (agora) => {
        const t = Math.min(1, (agora - inicio) / duracao);
        const suave = 1 - Math.pow(1 - t, 3);
        el.textContent = `${Math.round(alvo * suave)}${t === 1 ? sufixo : ""}`;
        if (t < 1)
            requestAnimationFrame(passo);
    };
    requestAnimationFrame(passo);
}
/** Dá a cada item um índice para a entrada em cascata definida no CSS. */
export function emCascata(raiz, seletor) {
    $$(seletor, raiz).forEach((el, i) => el.style.setProperty("--i", String(Math.min(i, 12))));
}
/** Linhas cinzas pulsando enquanto os dados carregam. */
export function esqueleto(linhas = 5) {
    const linha = '<div class="esq-linha"><span class="esq esq-bola"></span><span class="esq esq-a"></span><span class="esq esq-b"></span><span class="esq esq-c"></span></div>';
    return `<div class="esqueleto" aria-busy="true" aria-label="Carregando">${linha.repeat(linhas)}</div>`;
}
