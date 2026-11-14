import { api } from "../api.js";
import {
  abrirFormulario, abrirGaveta, avisarErro, botaoAcao, confirmar, montarPagina, paginador,
  painelErro, painelVazio, preencherPainel, tabela, voltouPagina, type Campo,
} from "../componentes.js";
import { pagina, porId } from "../dados.js";
import { $, $$, avatar, cep, esc, fone, toast } from "../dom.js";
import { paginaAtual } from "../estado.js";
import { PATA } from "../icones.js";
import { recarregar } from "../router.js";
import type { Animal, Tutor } from "../types.js";
import { abrirFicha } from "./animais.js";

const CAMPOS_TUTOR: Campo[] = [
  { nome: "nome", rotulo: "Nome completo", maxlength: 100, larga: true },
  { nome: "email", rotulo: "E-mail", tipo: "email", maxlength: 150 },
  { nome: "telefone", rotulo: "Telefone", tipo: "tel", maxlength: 11, pattern: "\\d{10,11}", inputmode: "numeric", ajuda: "Só números, com DDD." },
  { nome: "endereco", rotulo: "Endereço", maxlength: 200, larga: true, placeholder: "Rua das Flores" },
  { nome: "numero", rotulo: "Número", maxlength: 10, ajuda: "Use S/N se não houver número." },
  { nome: "complemento", rotulo: "Complemento", opcional: true, placeholder: "Apto, bloco, casa" },
  { nome: "cep", rotulo: "CEP", maxlength: 8, pattern: "\\d{8}", inputmode: "numeric", ajuda: "Só os 8 números." },
];

/** Monta "Rua X, 123" e a linha de baixo com complemento e CEP. */
function enderecoHTML(t: Tutor): string {
  if (!t.endereco) return "—";
  const linha = [t.endereco, t.numero].filter(Boolean).join(", ");
  const sub = [t.complemento, t.cep ? `CEP ${cep(t.cep)}` : ""].filter(Boolean).join(", ");
  return `${esc(linha)}${sub ? `<span class="sub">${esc(sub)}</span>` : ""}`;
}

export async function verTutores(): Promise<void> {
  montarPagina({ titulo: "Tutores", descricao: "Os responsáveis por cada paciente.", botao: "Novo tutor", aoClicar: () => formTutor() });

  let lista: Tutor[];
  try {
    lista = await api<Tutor[]>(`/tutores?${pagina(paginaAtual())}`);
  } catch (e) {
    painelErro(e);
    return;
  }
  if (voltouPagina(lista)) return;
  if (lista.length === 0) {
    painelVazio("Nenhum tutor cadastrado", "Cadastre o primeiro tutor para depois registrar os animais dele.", "Cadastrar tutor", () => formTutor());
    return;
  }

  const mapa = porId(lista);
  const linhas = lista.map((t) => `
    <tr>
      <td><div class="quem">${avatar(t.nome)}<div><strong>${esc(t.nome)}</strong><span class="sub">${esc(t.email)}</span></div></div></td>
      <td>${esc(fone(t.telefone))}</td>
      <td>${enderecoHTML(t)}</td>
      <td><div class="actions">${botaoAcao("animais", t.id, "Animais")}${botaoAcao("editar", t.id, "Editar")}${botaoAcao("excluir", t.id, "Excluir", true)}</div></td>
    </tr>`).join("");

  const com = (id: number, fn: (t: Tutor) => void): void => {
    const t = mapa.get(id);
    if (t) fn(t);
  };
  preencherPainel(tabela(["Tutor", "Telefone", "Endereço", ""], linhas) + paginador(lista.length), {
    animais: (id) => com(id, (t) => void animaisDoTutor(t)),
    editar: (id) => com(id, formTutor),
    excluir: (id) => com(id, (t) => void excluirTutor(t)),
  });
}

function formTutor(tutor?: Tutor): void {
  abrirFormulario({
    titulo: tutor ? "Editar tutor" : "Novo tutor",
    campos: CAMPOS_TUTOR,
    valores: tutor ? { ...tutor } : {},
    botao: tutor ? "Salvar alterações" : "Cadastrar tutor",
    enviar: async (dados) => {
      if (tutor) {
        await api(`/tutores/${tutor.id}`, { metodo: "PATCH", json: dados });
        toast("Tutor atualizado.");
      } else {
        await api("/tutores", { metodo: "POST", json: dados });
        toast("Tutor cadastrado.");
      }
      recarregar();
    },
  });
}

async function excluirTutor(tutor: Tutor): Promise<void> {
  const ok = await confirmar({
    titulo: `Excluir ${tutor.nome}?`,
    texto: "Os animais deste tutor e todo o histórico deles também serão excluídos. Não dá para desfazer.",
    botao: "Excluir tutor",
  });
  if (!ok) return;
  try {
    await api(`/tutores/${tutor.id}`, { metodo: "DELETE" });
    toast("Tutor excluído.");
    recarregar();
  } catch (e) {
    avisarErro(e);
  }
}

async function animaisDoTutor(tutor: Tutor): Promise<void> {
  const topo = `<div class="ficha-top">${PATA.replace("<svg", '<svg class="paws"')}<button type="button" class="x" data-fechar aria-label="Fechar">×</button><h2>${esc(tutor.nome)}</h2><p>${esc(tutor.email)}, ${esc(fone(tutor.telefone))}</p></div>`;
  const dlg = abrirGaveta(`<div class="ficha">${topo}<p class="loading">Carregando…</p></div>`);

  let animais: Animal[];
  try {
    animais = await api<Animal[]>(`/tutores/${tutor.id}/animais`);
  } catch (e) {
    dlg.close();
    avisarErro(e);
    return;
  }

  const corpo = animais.length
    ? `<ul class="lista-animais">${animais.map((a) => `<li><div><strong>${esc(a.nome)}</strong><small>${esc(a.especie)}, ${esc(a.raca)}</small></div><button class="btn ghost small" type="button" data-ficha="${a.id}">Abrir ficha</button></li>`).join("")}</ul>`
    : `<div class="empty"><h2>Nenhum animal</h2><p>Este tutor ainda não tem animais cadastrados.</p></div>`;
  $(".loading", dlg).outerHTML = `<h3 class="secao-titulo">Animais</h3>${corpo}`;

  const mapa = porId(animais);
  $$<HTMLButtonElement>("[data-ficha]", dlg).forEach((b) =>
    b.addEventListener("click", () => {
      const animal = mapa.get(Number(b.dataset["ficha"]));
      if (animal) void abrirFicha(animal, tutor);
    }),
  );
}
