import { api } from "../api.js";
import {
  abrirFormulario, abrirGaveta, avisarErro, botaoAcao, confirmar, montarPagina, paginador,
  painelErro, painelVazio, preencherPainel, tabela, voltouPagina,
} from "../componentes.js";
import { carregarTutores, pagina, porId } from "../dados.js";
import { $, avatar, badgePagamento, badgeTipo, brl, dataBR, dataISO, diaMes, esc, kg, sexo, toast } from "../dom.js";
import { estado, paginaAtual } from "../estado.js";
import { ICONES, PATA } from "../icones.js";
import { irPara, recarregar } from "../router.js";
import type { Animal, Procedimento, Tutor } from "../types.js";
import { formProcedimento } from "./procedimentos.js";

export async function verAnimais(): Promise<void> {
  montarPagina({ titulo: "Animais", descricao: "Os pacientes da clínica.", botao: "Novo animal", aoClicar: () => void formAnimal() });

  let lista: Animal[];
  let tutores: Tutor[];
  try {
    [lista, tutores] = await Promise.all([api<Animal[]>(`/animais?${pagina(paginaAtual())}`), carregarTutores()]);
  } catch (e) {
    painelErro(e);
    return;
  }
  if (voltouPagina(lista)) return;
  if (lista.length === 0) {
    if (tutores.length) painelVazio("Nenhum animal cadastrado", "Cadastre o primeiro paciente e vincule ao tutor dele.", "Cadastrar animal", () => void formAnimal(undefined, tutores));
    else painelVazio("Nenhum animal cadastrado", "Antes de cadastrar um animal, cadastre o tutor responsável por ele.", "Ir para tutores", () => irPara("tutores"));
    return;
  }

  const tutorPorId = porId(tutores);
  const mapa = porId(lista);
  const linhas = lista.map((a) => `
    <tr>
      <td><div class="quem">${avatar(a.nome, { pata: true })}<div><strong>${esc(a.nome)}</strong><span class="sub">${esc(a.especie)}, ${esc(a.raca)}</span></div></div></td>
      <td>${esc(sexo(a.sexo))}</td>
      <td>${esc(a.idade)}</td>
      <td class="num">${kg(a.peso)}</td>
      <td>${esc(tutorPorId.get(a.id_tutor)?.nome ?? "—")}</td>
      <td><div class="actions">${botaoAcao("ficha", a.id, "Ficha")}${botaoAcao("editar", a.id, "Editar")}${botaoAcao("excluir", a.id, "Excluir", true)}</div></td>
    </tr>`).join("");

  const com = (id: number, fn: (a: Animal) => void): void => {
    const a = mapa.get(id);
    if (a) fn(a);
  };
  preencherPainel(tabela(["Paciente", "Sexo", "Idade", { t: "Peso" }, "Tutor", ""], linhas) + paginador(lista.length), {
    ficha: (id) => com(id, (a) => void abrirFicha(a, tutorPorId.get(a.id_tutor))),
    editar: (id) => com(id, (a) => void formAnimal(a, tutores)),
    excluir: (id) => com(id, (a) => void excluirAnimal(a)),
  });
}

async function formAnimal(animal?: Animal, tutores?: Tutor[]): Promise<void> {
  let lista = tutores;
  try {
    lista ??= await carregarTutores();
  } catch (e) {
    avisarErro(e);
    return;
  }
  if (lista.length === 0) {
    toast("Cadastre um tutor antes de cadastrar um animal.", true);
    return;
  }

  abrirFormulario({
    titulo: animal ? `Editar ${animal.nome}` : "Novo animal",
    valores: animal ? { ...animal } : {},
    botao: animal ? "Salvar alterações" : "Cadastrar animal",
    campos: [
      { nome: "id_tutor", rotulo: "Tutor", tipo: "select", inteiro: true, larga: true, opcoes: lista.map((t) => ({ valor: t.id, rotulo: t.nome })) },
      { nome: "nome", rotulo: "Nome", maxlength: 100 },
      { nome: "especie", rotulo: "Espécie", maxlength: 50, placeholder: "Cachorro, gato…" },
      { nome: "raca", rotulo: "Raça", maxlength: 50 },
      { nome: "sexo", rotulo: "Sexo", tipo: "select", opcoes: [{ valor: "M", rotulo: "Macho" }, { valor: "F", rotulo: "Fêmea" }] },
      { nome: "idade", rotulo: "Idade", maxlength: 20, placeholder: "3 anos" },
      { nome: "peso", rotulo: "Peso (kg)", tipo: "number", min: 0.01, max: 499.99, step: 0.01, inputmode: "decimal" },
    ],
    enviar: async (dados) => {
      if (animal) {
        await api(`/animais/${animal.id}`, { metodo: "PATCH", json: dados });
        toast("Animal atualizado.");
      } else {
        await api("/animais", { metodo: "POST", json: dados });
        toast("Animal cadastrado.");
      }
      if (estado.view === "animais") recarregar();
    },
  });
}

async function excluirAnimal(animal: Animal): Promise<void> {
  const ok = await confirmar({
    titulo: `Excluir ${animal.nome}?`,
    texto: "Todo o histórico de procedimentos deste animal também será excluído. Não dá para desfazer.",
    botao: "Excluir animal",
  });
  if (!ok) return;
  try {
    await api(`/animais/${animal.id}`, { metodo: "DELETE" });
    toast("Animal excluído.");
    recarregar();
  } catch (e) {
    avisarErro(e);
  }
}

/** Itens da carteira de vacinação, com o selo de data. */
export function carteiraHTML(vacinas: Procedimento[]): string {
  if (vacinas.length === 0) return `<p class="vazio">Nenhuma vacina registrada ainda.</p>`;
  const hoje = dataISO();
  return `<ol>${vacinas.map((v) => {
    const { dia, mes } = diaMes(v.data);
    const agendada = v.data > hoje;
    return `<li><span class="selo${agendada ? " agendada" : ""}"><b>${dia}</b><small>${mes}</small></span><div><strong>${esc(v.nome)}</strong><small>${agendada ? "Agendada para" : "Aplicada em"} ${dataBR(v.data)}</small></div></li>`;
  }).join("")}</ol>`;
}

/** Linha do tempo de procedimentos. */
export function historicoHTML(procs: Procedimento[]): string {
  if (procs.length === 0) return `<p class="loading">Nenhum procedimento registrado.</p>`;
  const hoje = dataISO();
  return `<ol class="historico">${procs.map((p) => `
    <li class="${p.data > hoje ? "futuro" : ""}">
      <div class="quando">${dataBR(p.data)} ${badgeTipo(p.tipo)} ${badgePagamento(p.forma_pagamento)}</div>
      <strong>${esc(p.nome)}</strong>
      <p>${esc(p.descricao)}${p.preco != null ? ` (${brl(p.preco)})` : ""}</p>
    </li>`).join("")}</ol>`;
}

/** Ficha do animal: dados, carteira de vacinação e histórico. */
export async function abrirFicha(animal: Animal, tutor?: Tutor): Promise<void> {
  const topo = `<div class="ficha-top">${PATA.replace("<svg", '<svg class="paws"')}<button type="button" class="x" data-fechar aria-label="Fechar">×</button><h2>${esc(animal.nome)}</h2><p>${esc(animal.especie)}, ${esc(animal.raca)}${tutor ? `. Tutor: ${esc(tutor.nome)}` : ""}</p></div>`;
  const dlg = abrirGaveta(`<div class="ficha">${topo}<p class="loading">Carregando ficha…</p></div>`);

  let historico: Procedimento[];
  let vacinas: Procedimento[];
  try {
    [historico, vacinas] = await Promise.all([
      api<Procedimento[]>(`/animais/${animal.id}/procedimentos`),
      api<Procedimento[]>(`/animais/${animal.id}/vacinas`),
    ]);
  } catch (e) {
    dlg.close();
    avisarErro(e);
    return;
  }

  abrirGaveta(`<div class="ficha">${topo}
    <div class="dados">
      <div class="dado"><span>Sexo</span><strong>${esc(sexo(animal.sexo))}</strong></div>
      <div class="dado"><span>Idade</span><strong>${esc(animal.idade)}</strong></div>
      <div class="dado"><span>Peso</span><strong>${kg(animal.peso)}</strong></div>
    </div>
    <h3 class="secao-titulo">Carteira de vacinação</h3>
    <div class="carteira">${carteiraHTML(vacinas)}</div>
    <h3 class="secao-titulo">Histórico</h3>
    ${historicoHTML(historico)}
    <button class="btn" type="button" id="btn-agendar">${ICONES.mais}Agendar procedimento</button>
  </div>`);

  $("#btn-agendar", dlg).addEventListener("click", () => {
    dlg.close();
    void formProcedimento(undefined, undefined, animal.id);
  });
}
