import { api } from "../api.js";
import { abrirGaveta, painelErro } from "../componentes.js";
import { CONFIG } from "../config.js";
import { porId } from "../dados.js";
import { $, $$, avatar, badgePagamento, badgeTipo, brl, dataBR, dataISO, diaMes, emCascata, esc, esqueleto, kg, sexo } from "../dom.js";
import { estado } from "../estado.js";
import { PATA } from "../icones.js";
import type { Animal, Procedimento } from "../types.js";
import { carteiraHTML, historicoHTML } from "./animais.js";

/* Área do tutor: só leitura. A API devolve apenas os dados do tutor ligado à conta. */

const tudo = `skip=0&limit=${CONFIG.LIMITE_MAXIMO}`;
const meusAnimais = (): Promise<Animal[]> => api<Animal[]>(`/meus/animais?${tudo}`);
const meusProcedimentos = (): Promise<Procedimento[]> => api<Procedimento[]>(`/meus/procedimentos?${tudo}`);

export async function verMeusAnimais(): Promise<void> {
  const conteudo = $("#conteudo");
  const nome = estado.email.split("@")[0] ?? "";
  conteudo.innerHTML = `
    <section class="hero">${PATA.replace("<svg", '<svg class="paws"')}
      <h1>Olá, ${esc(nome)}</h1>
      <p>Aqui você acompanha os seus animais, as vacinas e os atendimentos na clínica.</p>
    </section>
    <div id="painel">${esqueleto(3)}</div>`;

  let animais: Animal[];
  let procs: Procedimento[];
  try {
    [animais, procs] = await Promise.all([meusAnimais(), meusProcedimentos()]);
  } catch (e) {
    painelErro(e);
    return;
  }

  const painel = $("#painel");
  if (animais.length === 0) {
    painel.innerHTML = `<div class="panel"><div class="empty"><h2>Nenhum animal cadastrado</h2><p>Quando a clínica cadastrar um animal no seu nome, ele aparece aqui.</p></div></div>`;
    return;
  }

  const hoje = dataISO();
  const cartoes = animais.map((a) => {
    const proximo = procs.filter((p) => p.id_animal === a.id && p.data >= hoje).sort((x, y) => x.data.localeCompare(y.data))[0];
    return `<button type="button" class="pet" data-animal="${a.id}">
      <span class="pet-topo">${avatar(a.nome, { pata: true })}<span><strong>${esc(a.nome)}</strong><small>${esc(a.especie)}, ${esc(a.raca)}</small></span></span>
      <span class="pet-dados"><span>${esc(sexo(a.sexo))}</span><span>${esc(a.idade)}</span><span>${kg(a.peso)}</span></span>
      <span class="pet-prox">${proximo ? `Próximo: ${esc(proximo.nome)} em ${dataBR(proximo.data)}` : "Nenhum atendimento agendado"}</span>
    </button>`;
  }).join("");

  painel.innerHTML = `<div class="pets">${cartoes}</div>`;
  emCascata(painel, ".pet");

  const mapa = porId(animais);
  $$<HTMLButtonElement>("[data-animal]", painel).forEach((b) =>
    b.addEventListener("click", () => {
      const animal = mapa.get(Number(b.dataset["animal"]));
      if (animal) fichaDoTutor(animal, procs.filter((p) => p.id_animal === animal.id));
    }),
  );
}

function fichaDoTutor(animal: Animal, procs: Procedimento[]): void {
  const emOrdem = [...procs].sort((a, b) => a.data.localeCompare(b.data));
  const vacinas = emOrdem.filter((p) => p.tipo === "Vacinação");
  abrirGaveta(`<div class="ficha">
    <div class="ficha-top">${PATA.replace("<svg", '<svg class="paws"')}<button type="button" class="x" data-fechar aria-label="Fechar">×</button><h2>${esc(animal.nome)}</h2><p>${esc(animal.especie)}, ${esc(animal.raca)}</p></div>
    <div class="dados">
      <div class="dado"><span>Sexo</span><strong>${esc(sexo(animal.sexo))}</strong></div>
      <div class="dado"><span>Idade</span><strong>${esc(animal.idade)}</strong></div>
      <div class="dado"><span>Peso</span><strong>${kg(animal.peso)}</strong></div>
    </div>
    <h3 class="secao-titulo">Carteira de vacinação</h3>
    <div class="carteira">${carteiraHTML(vacinas)}</div>
    <h3 class="secao-titulo">Histórico</h3>
    ${historicoHTML(emOrdem)}
  </div>`);
}

export async function verMeusProcedimentos(): Promise<void> {
  $("#conteudo").innerHTML = `
    <header class="page-head"><div><h1>Meus procedimentos</h1><p>Os atendimentos agendados e os que já aconteceram.</p></div></header>
    <div id="painel">${esqueleto(4)}</div>`;

  let animais: Animal[];
  let procs: Procedimento[];
  try {
    [animais, procs] = await Promise.all([meusAnimais(), meusProcedimentos()]);
  } catch (e) {
    painelErro(e);
    return;
  }

  const painel = $("#painel");
  if (procs.length === 0) {
    painel.innerHTML = `<div class="panel"><div class="empty"><h2>Nenhum procedimento cadastrado</h2><p>Quando a clínica agendar um atendimento para um dos seus animais, ele aparece aqui.</p></div></div>`;
    return;
  }

  const animalPorId = porId(animais);
  const hoje = dataISO();
  const proximos = procs.filter((p) => p.data >= hoje).sort((a, b) => a.data.localeCompare(b.data));
  const passados = procs.filter((p) => p.data < hoje).sort((a, b) => b.data.localeCompare(a.data));

  const item = (p: Procedimento): string => {
    const { dia, mes } = diaMes(p.data);
    const animal = animalPorId.get(p.id_animal);
    return `<li><span class="dia"><b>${dia}</b><small>${mes}</small></span>
      <div class="info"><strong>${esc(p.nome)}</strong><span>${esc(animal?.nome ?? "")}${p.preco != null ? `, ${brl(p.preco)}` : ""}</span></div>
      <span class="etiquetas">${badgeTipo(p.tipo)}${badgePagamento(p.forma_pagamento)}</span></li>`;
  };
  const bloco = (titulo: string, lista: Procedimento[], vazio: string): string =>
    `<section class="bloco"><h2>${titulo}</h2>${lista.length ? `<ol class="agenda">${lista.map(item).join("")}</ol>` : `<p class="vazio-curto">${vazio}</p>`}</section>`;

  painel.innerHTML = `<div class="pilha">
    ${bloco("Próximos", proximos, "Nenhum atendimento agendado.")}
    ${bloco("Já realizados", passados, "Nenhum atendimento anterior.")}
  </div>`;
  emCascata(painel, ".agenda li");
}
