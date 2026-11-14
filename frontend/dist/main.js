import { ApiError, api, aoExpirarSessao, ehErroApi, emailDoToken, mensagemDe } from "./api.js";
import { fecharDialogos } from "./componentes.js";
import { CONFIG } from "./config.js";
import { $, $$, corAvatar, iniciais, toast } from "./dom.js";
import { estado, guardar, lerGuardado } from "./estado.js";
import { ICONES } from "./icones.js";
import { irPara, montarNav, registrar } from "./router.js";
import { verAnimais } from "./views/animais.js";
import { verInicio } from "./views/inicio.js";
import { verMeusAnimais, verMeusProcedimentos } from "./views/portal.js";
import { verProcedimentos } from "./views/procedimentos.js";
import { verTutores } from "./views/tutores.js";
import { verUsuarios } from "./views/usuarios.js";
/* ===== Telas do menu ===== */
registrar("inicio", { titulo: "Início", icone: "inicio", grupo: "Visão geral", papel: "equipe", render: verInicio });
registrar("tutores", { titulo: "Tutores", icone: "tutores", grupo: "Cadastros", papel: "equipe", render: verTutores });
registrar("animais", { titulo: "Animais", icone: "animais", grupo: "Cadastros", papel: "equipe", render: verAnimais });
registrar("procedimentos", { titulo: "Procedimentos", icone: "procedimentos", grupo: "Atendimento", papel: "equipe", render: verProcedimentos });
registrar("usuarios", { titulo: "Usuários", icone: "usuarios", grupo: "Administração", papel: "equipe", admin: true, render: verUsuarios });
registrar("meusAnimais", { titulo: "Meus animais", icone: "animais", grupo: "Meu espaço", papel: "tutor", render: verMeusAnimais });
registrar("meusProcedimentos", { titulo: "Meus procedimentos", icone: "agenda", grupo: "Meu espaço", papel: "tutor", render: verMeusProcedimentos });
function mostrarTela(id) {
    ["tela-login", "tela-aguardando", "tela-app"].forEach((t) => {
        $(`#${t}`).hidden = t !== id;
    });
}
/* ===== Sessão ===== */
function sair(mensagem) {
    estado.token = null;
    estado.email = "";
    estado.admin = false;
    estado.pagina = {};
    guardar("vetsys_token", null);
    fecharDialogos();
    mostrarTela("tela-login");
    if (mensagem)
        toast(mensagem, true);
}
aoExpirarSessao(() => sair("Sua sessão expirou. Entre de novo."));
async function entrar(email, senha) {
    const r = await api("/auth/login", { metodo: "POST", form: { username: email, password: senha }, publica: true });
    estado.token = r.access_token;
    estado.email = emailDoToken(r.access_token) || email;
    guardar("vetsys_token", estado.token);
    await iniciar();
}
/** Responde se a rota aceita a conta logada (200) ou recusa por permissão (403). */
async function podeAcessar(caminho) {
    try {
        await api(caminho);
        return true;
    }
    catch (e) {
        if (ehErroApi(e) && e.status === 403)
            return false;
        throw e;
    }
}
/** Descobre o perfil da conta testando as rotas, e abre a área certa. */
async function iniciar() {
    try {
        if (await podeAcessar("/tutores?skip=0&limit=1")) {
            estado.papel = "equipe";
            estado.admin = await podeAcessar(`${CONFIG.ADMIN.listar}?skip=0&limit=1`);
        }
        else if (await podeAcessar("/meus/animais?skip=0&limit=1")) {
            estado.papel = "tutor";
            estado.admin = false;
        }
        else {
            $("#aguardando-email").textContent = estado.email;
            mostrarTela("tela-aguardando");
            return;
        }
    }
    catch (e) {
        if (e instanceof ApiError && e.status === 401)
            return;
        mostrarTela("tela-login");
        toast(mensagemDe(e), true);
        return;
    }
    $("#usuario-email").textContent = estado.email;
    $("#usuario-papel").textContent = estado.papel === "tutor" ? "Tutor" : estado.admin ? "Administrador" : "Equipe";
    const av = $("#usuario-avatar");
    av.textContent = iniciais(estado.email);
    av.className = `avatar redondo ${corAvatar(estado.email)}`;
    mostrarTela("tela-app");
    montarNav();
    irPara(estado.view);
}
function temaAtual() {
    const forcado = document.documentElement.dataset["theme"];
    if (forcado === "dark" || forcado === "light")
        return forcado;
    return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
function desenharBotoesTema() {
    const escuro = temaAtual() === "dark";
    $$("[data-tema]").forEach((b) => {
        b.innerHTML = `${escuro ? ICONES.sol : ICONES.lua}<span>${escuro ? "Tema claro" : "Tema escuro"}</span>`;
    });
}
function aplicarTema(tema) {
    const raiz = document.documentElement;
    // Suaviza a troca de cores só durante a mudança de tema.
    raiz.classList.add("trocando-tema");
    raiz.dataset["theme"] = tema;
    setTimeout(() => raiz.classList.remove("trocando-tema"), 400);
    try {
        localStorage.setItem("vetsys_tema", tema);
    }
    catch {
        /* sem armazenamento: o tema vale só nesta visita */
    }
    desenharBotoesTema();
}
function iniciarTema() {
    try {
        const salvo = localStorage.getItem("vetsys_tema");
        if (salvo === "dark" || salvo === "light")
            document.documentElement.dataset["theme"] = salvo;
    }
    catch {
        /* segue o tema do sistema */
    }
    $$("[data-tema]").forEach((b) => b.addEventListener("click", () => aplicarTema(temaAtual() === "dark" ? "light" : "dark")));
    desenharBotoesTema();
}
/* ===== Login e cadastro ===== */
function trocarAba(qual) {
    const entrando = qual === "entrar";
    $("#aba-entrar").setAttribute("aria-selected", String(entrando));
    $("#aba-criar").setAttribute("aria-selected", String(!entrando));
    $("#form-entrar").hidden = !entrando;
    $("#form-criar").hidden = entrando;
}
/** Liga um formulário de acesso: trava o botão, mostra o erro no próprio formulário. */
function ligarFormulario(id, acao) {
    const form = $(id);
    form.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        const erro = $(".form-erro", form);
        const botao = $("button[type=submit]", form);
        erro.hidden = true;
        botao.disabled = true;
        try {
            await acao(form);
            form.reset();
        }
        catch (e) {
            erro.textContent = mensagemDe(e);
            erro.hidden = false;
        }
        finally {
            botao.disabled = false;
        }
    });
}
const campo = (form, nome) => form.elements.namedItem(nome).value;
function iniciarAcesso() {
    $("#aba-entrar").addEventListener("click", () => trocarAba("entrar"));
    $("#aba-criar").addEventListener("click", () => trocarAba("criar"));
    ligarFormulario("#form-entrar", (form) => entrar(campo(form, "email").trim(), campo(form, "senha")));
    ligarFormulario("#form-criar", async (form) => {
        const dados = { nome: campo(form, "nome").trim(), email: campo(form, "email").trim(), senha: campo(form, "senha") };
        await api("/auth/registro", { metodo: "POST", json: dados, publica: true });
        toast("Conta criada.");
        await entrar(dados.email, dados.senha);
        trocarAba("entrar");
    });
    $("#btn-sair").addEventListener("click", () => sair());
    $("#btn-sair-aguardando").addEventListener("click", () => sair());
    $("#btn-verificar").addEventListener("click", () => void iniciar());
}
/* ===== Início ===== */
iniciarTema();
iniciarAcesso();
const tokenSalvo = lerGuardado("vetsys_token");
if (tokenSalvo) {
    estado.token = tokenSalvo;
    estado.email = emailDoToken(tokenSalvo);
    void iniciar();
}
else {
    mostrarTela("tela-login");
}
