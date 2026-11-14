import { ehErroApi, mensagemDe } from "./api.js";
import { $, $$, emCascata, esc, esqueleto, toast } from "./dom.js";
import { estado, paginaAtual } from "./estado.js";
import { CONFIG } from "./config.js";
import { ICONES } from "./icones.js";
import { recarregar } from "./router.js";
export function montarPagina({ titulo, descricao, botao, aoClicar, busca = true }) {
    $("#conteudo").innerHTML = `
    <header class="page-head">
      <div><h1>${esc(titulo)}</h1><p>${esc(descricao)}</p></div>
      <div class="toolbar">
        ${busca ? `<label class="search">${ICONES.busca}<input type="search" id="busca" placeholder="Buscar nesta página" aria-label="Buscar nesta página"></label>` : ""}
        ${botao ? `<button class="btn" type="button" id="btn-novo">${ICONES.mais}${esc(botao)}</button>` : ""}
      </div>
    </header>
    <div class="panel" id="painel">${esqueleto()}</div>`;
    if (botao && aoClicar)
        $("#btn-novo").addEventListener("click", aoClicar);
    if (busca) {
        $("#busca").addEventListener("input", (e) => {
            const q = e.target.value.trim().toLowerCase();
            $$("#painel tbody tr").forEach((tr) => {
                tr.hidden = Boolean(q) && !(tr.textContent ?? "").toLowerCase().includes(q);
            });
        });
    }
}
export function tabela(colunas, linhas) {
    const ths = colunas.map((c) => (typeof c === "string" ? `<th>${c}</th>` : `<th class="num">${c.t}</th>`)).join("");
    return `<div class="table-wrap"><table><thead><tr>${ths}</tr></thead><tbody>${linhas}</tbody></table></div>`;
}
export function paginador(quantidade) {
    const p = paginaAtual();
    return `<footer class="pager"><span>Página ${p + 1}</span><div>
    <button class="btn ghost small" type="button" data-pag="-1" ${p === 0 ? "disabled" : ""}>Anterior</button>
    <button class="btn ghost small" type="button" data-pag="1" ${quantidade < CONFIG.LIMITE ? "disabled" : ""}>Próxima</button>
  </div></footer>`;
}
/** Coloca o conteúdo no painel e liga os botões de ação e de paginação. */
export function preencherPainel(html, acoes = {}) {
    const painel = $("#painel");
    painel.innerHTML = html;
    emCascata(painel, "tbody tr");
    $$("[data-pag]", painel).forEach((b) => b.addEventListener("click", () => {
        estado.pagina[estado.view] = paginaAtual() + Number(b.dataset["pag"]);
        recarregar();
    }));
    $$("[data-acao]", painel).forEach((b) => b.addEventListener("click", () => acoes[b.dataset["acao"] ?? ""]?.(Number(b.dataset["id"]))));
}
export function painelVazio(titulo, texto, botao, aoClicar) {
    $("#painel").innerHTML = `<div class="empty"><h2>${esc(titulo)}</h2><p>${esc(texto)}</p>${botao ? `<button class="btn" type="button" id="btn-vazio">${esc(botao)}</button>` : ""}</div>`;
    if (botao && aoClicar)
        $("#btn-vazio").addEventListener("click", aoClicar);
}
export function painelErro(e) {
    if (ehErroApi(e) && e.status === 401)
        return; // a sessão já foi encerrada e avisada
    $("#painel").innerHTML = `<div class="empty"><h2>Não foi possível carregar</h2><p>${esc(mensagemDe(e))}</p><button class="btn ghost" type="button" id="btn-tentar">Tentar de novo</button></div>`;
    $("#btn-tentar").addEventListener("click", recarregar);
}
/** Se a página atual ficou vazia (o último item foi excluído), volta uma página. */
export function voltouPagina(lista) {
    if (lista.length === 0 && paginaAtual() > 0) {
        estado.pagina[estado.view] = paginaAtual() - 1;
        recarregar();
        return true;
    }
    return false;
}
export function botaoAcao(acao, id, texto, perigo = false) {
    return `<button class="link${perigo ? " danger" : ""}" type="button" data-acao="${acao}" data-id="${id}">${texto}</button>`;
}
/** Mostra o erro de uma ação num aviso, a menos que seja sessão expirada. */
export function avisarErro(e) {
    if (ehErroApi(e) && e.status === 401)
        return;
    toast(mensagemDe(e), true);
}
function campoHTML(c, valores) {
    const v = valores[c.nome] ?? "";
    const id = `campo-${c.nome}`;
    const obrigatorio = c.opcional ? "" : "required";
    let controle;
    if (c.tipo === "select") {
        const opcoes = (c.opcoes ?? [])
            .map((o) => `<option value="${esc(o.valor)}" ${String(o.valor) === String(v) ? "selected" : ""}>${esc(o.rotulo)}</option>`)
            .join("");
        const primeira = c.vazio
            ? `<option value="" ${v === "" ? "selected" : ""}>${esc(c.vazio)}</option>`
            : `<option value="" disabled ${v === "" ? "selected" : ""}>Escolha…</option>`;
        controle = `<select id="${id}" name="${c.nome}" ${obrigatorio}>${primeira}${opcoes}</select>`;
    }
    else if (c.tipo === "textarea") {
        controle = `<textarea id="${id}" name="${c.nome}" ${c.maxlength ? `maxlength="${c.maxlength}"` : ""} ${obrigatorio}>${esc(v)}</textarea>`;
    }
    else {
        const attrs = [
            `type="${c.tipo ?? "text"}"`,
            c.maxlength ? `maxlength="${c.maxlength}"` : "",
            c.min !== undefined ? `min="${c.min}"` : "",
            c.max !== undefined ? `max="${c.max}"` : "",
            c.step ? `step="${c.step}"` : "",
            c.pattern ? `pattern="${c.pattern}"` : "",
            c.inputmode ? `inputmode="${c.inputmode}"` : "",
            c.placeholder ? `placeholder="${esc(c.placeholder)}"` : "",
        ].join(" ");
        controle = `<input id="${id}" name="${c.nome}" value="${esc(v)}" ${attrs} ${obrigatorio}>`;
    }
    return `<div class="field${c.larga ? " full" : ""}"><label for="${id}">${esc(c.rotulo)}</label>${controle}${c.ajuda ? `<small>${esc(c.ajuda)}</small>` : ""}</div>`;
}
export function abrirFormulario({ titulo, campos, valores = {}, botao, enviar }) {
    const dlg = $("#dlg-form");
    dlg.innerHTML = `
    <form id="form-modal">
      <div class="dlg-head"><h2>${esc(titulo)}</h2><button type="button" class="x" data-fechar aria-label="Fechar">×</button></div>
      <div class="dlg-body"><div class="form-erro" hidden></div><div class="form-grid">${campos.map((c) => campoHTML(c, valores)).join("")}</div></div>
      <div class="dlg-foot"><button type="button" class="btn ghost" data-fechar>Cancelar</button><button type="submit" class="btn">${esc(botao)}</button></div>
    </form>`;
    $$("[data-fechar]", dlg).forEach((b) => b.addEventListener("click", () => dlg.close()));
    const form = $("#form-modal", dlg);
    form.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        const erro = $(".form-erro", form);
        const enviarBtn = $("button[type=submit]", form);
        const dados = {};
        for (const c of campos) {
            const controle = form.elements.namedItem(c.nome);
            const texto = c.tipo === "select" ? controle.value : controle.value.trim();
            if (texto === "") {
                // Campo opcional apagado numa edição: envia null para limpar. Vazio desde o início: não envia.
                const tinhaValor = (valores[c.nome] ?? "") !== "";
                if (c.opcional && tinhaValor)
                    dados[c.nome] = null;
                continue;
            }
            dados[c.nome] = c.tipo === "number" || c.inteiro ? Number(texto) : texto;
        }
        erro.hidden = true;
        enviarBtn.disabled = true;
        try {
            await enviar(dados);
            dlg.close();
        }
        catch (e) {
            if (ehErroApi(e) && e.status === 401)
                return;
            erro.textContent = mensagemDe(e);
            erro.hidden = false;
        }
        finally {
            enviarBtn.disabled = false;
        }
    });
    dlg.showModal();
    form.querySelector("input, select, textarea")?.focus();
}
/* ===== Confirmação ===== */
export function confirmar(opcoes) {
    return new Promise((resolver) => {
        const dlg = $("#dlg-confirma");
        dlg.innerHTML = `
      <div class="dlg-head"><h2>${esc(opcoes.titulo)}</h2><button type="button" class="x" data-r="nao" aria-label="Fechar">×</button></div>
      <div class="dlg-body"><p>${esc(opcoes.texto)}</p></div>
      <div class="dlg-foot"><button type="button" class="btn ghost" data-r="nao">Cancelar</button><button type="button" class="btn danger" data-r="sim">${esc(opcoes.botao)}</button></div>`;
        let resposta = false;
        $$("[data-r]", dlg).forEach((b) => b.addEventListener("click", () => {
            resposta = b.dataset["r"] === "sim";
            dlg.close();
        }));
        dlg.addEventListener("close", () => resolver(resposta), { once: true });
        dlg.showModal();
        $("[data-r=nao].btn", dlg).focus();
    });
}
/* ===== Painel lateral (ficha) ===== */
export function abrirGaveta(html) {
    const dlg = $("#dlg-ficha");
    dlg.innerHTML = html;
    $$("[data-fechar]", dlg).forEach((b) => b.addEventListener("click", () => dlg.close()));
    if (!dlg.open)
        dlg.showModal();
    return dlg;
}
export function fecharDialogos() {
    $$("dialog[open]").forEach((d) => d.close());
}
