import { $, $$ } from "./dom.js";
import { estado } from "./estado.js";
import { ICONES, type NomeIcone } from "./icones.js";
import type { Papel } from "./types.js";

export interface View {
  titulo: string;
  icone: NomeIcone;
  /** Seção do menu em que a tela aparece. */
  grupo: string;
  papel: Papel;
  /** Só administradores enxergam. */
  admin?: boolean;
  render: () => void | Promise<void>;
}

const views = new Map<string, View>();

export function registrar(chave: string, view: View): void {
  views.set(chave, view);
}

function visiveis(): [string, View][] {
  return [...views].filter(([, v]) => v.papel === estado.papel && (!v.admin || estado.admin));
}

/** Monta o menu lateral, agrupando as telas por seção. */
export function montarNav(): void {
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
  $$<HTMLButtonElement>("button", nav).forEach((b) => b.addEventListener("click", () => irPara(b.dataset["view"])));
}

/** Desliza o marcador do menu até o item ativo. */
function moverMarca(): void {
  const nav = $("#nav");
  const ativo = nav.querySelector<HTMLElement>('button[aria-current="page"]');
  const marca = nav.querySelector<HTMLElement>(".nav-marca");
  if (!ativo || !marca) return;
  marca.style.width = `${ativo.offsetWidth}px`;
  marca.style.height = `${ativo.offsetHeight}px`;
  marca.style.transform = `translate(${ativo.offsetLeft}px, ${ativo.offsetTop}px)`;
  marca.classList.add("visivel");
}

export function irPara(chave?: string): void {
  const disponiveis = visiveis();
  const destino = disponiveis.find(([c]) => c === chave) ?? disponiveis[0];
  if (!destino) return;
  const [nome, view] = destino;
  estado.view = nome;

  $$("button", $("#nav")).forEach((b) => {
    if (b.dataset["view"] === nome) b.setAttribute("aria-current", "page");
    else b.removeAttribute("aria-current");
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
export function recarregar(): void {
  irPara(estado.view);
}

window.addEventListener("resize", moverMarca);
