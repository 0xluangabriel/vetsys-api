import { $, $$ } from "./dom.js";
import { estado } from "./estado.js";
import { ICONES } from "./icones.js";
const views = new Map();
export function registrar(chave, view) {
    views.set(chave, view);
}
function visiveis() {
    return [...views].filter(([, v]) => v.papel === estado.papel && (!v.admin || estado.admin));
}
/** Monta o menu lateral, agrupando as telas por seção. */
export function montarNav() {
    const nav = $("#nav");
    let html = '<span class="nav-marca" aria-hidden="true"></span>';
    let grupoAtual = "";
    for (const [chave, v] of visiveis()) {
        if (v.grupo !== grupoAtual) {
            grupoAtual = v.grupo;
            html += `<p class="nav-grupo">${grupoAtual}</p>`;
        }
        html += `<button type="button" data-view="${chave}">${ICONES[v.icone]}<span>${v.titulo}</span></button>`;
    }
    nav.innerHTML = html;
    $$("button", nav).forEach((b) => b.addEventListener("click", () => irPara(b.dataset["view"])));
}
/** Desliza o marcador do menu até o item ativo. */
function moverMarca() {
    const nav = $("#nav");
    const ativo = nav.querySelector('button[aria-current="page"]');
    const marca = nav.querySelector(".nav-marca");
    if (!ativo || !marca)
        return;
    marca.style.width = `${ativo.offsetWidth}px`;
    marca.style.height = `${ativo.offsetHeight}px`;
    marca.style.transform = `translate(${ativo.offsetLeft}px, ${ativo.offsetTop}px)`;
    marca.classList.add("visivel");
}
export function irPara(chave) {
    const disponiveis = visiveis();
    const destino = disponiveis.find(([c]) => c === chave) ?? disponiveis[0];
    if (!destino)
        return;
    const [nome, view] = destino;
    estado.view = nome;
    $$("button", $("#nav")).forEach((b) => {
        if (b.dataset["view"] === nome)
            b.setAttribute("aria-current", "page");
        else
            b.removeAttribute("aria-current");
    });
    moverMarca();
    // Reinicia a animação de entrada do conteúdo.
    const conteudo = $("#conteudo");
    conteudo.classList.remove("entrando");
    void conteudo.offsetWidth;
    conteudo.classList.add("entrando");
    void view.render();
}
/** Redesenha a tela atual (depois de salvar ou excluir algo). */
export function recarregar() {
    irPara(estado.view);
}
window.addEventListener("resize", moverMarca);
