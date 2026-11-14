import { api } from "../api.js";
import {
  abrirFormulario, avisarErro, botaoAcao, confirmar, montarPagina, paginador,
  painelErro, painelVazio, preencherPainel, tabela, voltouPagina,
} from "../componentes.js";
import { CONFIG } from "../config.js";
import { carregarTutores, pagina, porId } from "../dados.js";
import { avatar, badgePerfil, esc, toast } from "../dom.js";
import { estado, paginaAtual } from "../estado.js";
import { recarregar } from "../router.js";
import type { Tutor, UsuarioAdmin } from "../types.js";

export async function verUsuarios(): Promise<void> {
  montarPagina({ titulo: "Usuários", descricao: "Quem tem acesso ao painel e com qual perfil." });

  let lista: UsuarioAdmin[];
  try {
    lista = await api<UsuarioAdmin[]>(`${CONFIG.ADMIN.listar}?${pagina(paginaAtual())}`);
  } catch (e) {
    painelErro(e);
    return;
  }
  if (voltouPagina(lista)) return;
  if (lista.length === 0) {
    painelVazio("Nenhum usuário", "Quando alguém criar uma conta, ela aparece aqui.");
    return;
  }

  const mapa = porId(lista);
  const linhas = lista.map((u) => {
    const eu = u.email === estado.email;
    let acoes = "";
    if (!eu) {
      // Sem o perfil na resposta da API, todas as ações ficam disponíveis.
      const perfil = u.perfil;
      if (!perfil || perfil === "comum") {
        acoes += botaoAcao("promover", u.id, "Liberar acesso");
        acoes += botaoAcao("vincular", u.id, "Vincular a tutor");
      }
      if (!perfil || perfil !== "comum") acoes += botaoAcao("rebaixar", u.id, "Remover acesso");
      acoes += botaoAcao("excluir", u.id, "Excluir", true);
    }
    return `<tr>
      <td><div class="quem">${avatar(u.email, { redondo: true })}<div><strong>${esc(u.nome)}</strong>${eu ? '<span class="sub">Você</span>' : ""}</div></div></td>
      <td>${esc(u.email)}</td>
      <td>${badgePerfil(u.perfil)}</td>
      <td><div class="actions">${acoes}</div></td>
    </tr>`;
  }).join("");

  const com = (id: number, fn: (u: UsuarioAdmin) => void): void => {
    const u = mapa.get(id);
    if (u) fn(u);
  };
  preencherPainel(tabela(["Nome", "E-mail", "Perfil", ""], linhas) + paginador(lista.length), {
    promover: (id) => com(id, (u) => void alterarAcesso(u, "promover")),
    rebaixar: (id) => com(id, (u) => void alterarAcesso(u, "rebaixar")),
    vincular: (id) => com(id, (u) => void vincularTutor(u)),
    excluir: (id) => com(id, (u) => void excluirUsuario(u)),
  });
}

async function alterarAcesso(usuario: UsuarioAdmin, acao: "promover" | "rebaixar"): Promise<void> {
  try {
    await api(CONFIG.ADMIN[acao](usuario.id), { metodo: "PATCH" });
    toast(acao === "promover" ? `${usuario.nome} agora tem acesso de funcionário.` : `${usuario.nome} não tem mais acesso aos dados.`);
    recarregar();
  } catch (e) {
    avisarErro(e);
  }
}

/** Liga a conta a um tutor cadastrado: ela passa a ver só os animais dele. */
async function vincularTutor(usuario: UsuarioAdmin): Promise<void> {
  let tutores: Tutor[];
  try {
    tutores = await carregarTutores();
  } catch (e) {
    avisarErro(e);
    return;
  }
  if (tutores.length === 0) {
    toast("Cadastre o tutor antes de vincular a conta.", true);
    return;
  }

  abrirFormulario({
    titulo: `Vincular ${usuario.nome} a um tutor`,
    botao: "Vincular conta",
    campos: [{
      nome: "id_tutor", rotulo: "Tutor", tipo: "select", inteiro: true, larga: true,
      opcoes: tutores.map((t) => ({ valor: t.id, rotulo: `${t.nome} (${t.email})` })),
      ajuda: "Confira a identidade da pessoa antes de vincular. A conta vai ver os animais e os procedimentos deste tutor.",
    }],
    enviar: async (dados) => {
      await api(CONFIG.ADMIN.vincular(usuario.id), { metodo: "PATCH", json: dados });
      toast(`${usuario.nome} agora acessa como tutor.`);
      recarregar();
    },
  });
}

async function excluirUsuario(usuario: UsuarioAdmin): Promise<void> {
  const ok = await confirmar({
    titulo: `Excluir a conta de ${usuario.nome}?`,
    texto: "A pessoa perde o acesso ao painel na hora. Não dá para desfazer.",
    botao: "Excluir conta",
  });
  if (!ok) return;
  try {
    await api(CONFIG.ADMIN.excluir(usuario.id), { metodo: "DELETE" });
    toast("Conta excluída.");
    recarregar();
  } catch (e) {
    avisarErro(e);
  }
}
