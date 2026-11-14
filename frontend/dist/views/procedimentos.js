import { api } from "../api.js";
import { abrirFormulario, avisarErro, botaoAcao, confirmar, montarPagina, paginador, painelErro, painelVazio, preencherPainel, tabela, voltouPagina, } from "../componentes.js";
import { carregarAnimais, pagina, porId } from "../dados.js";
import { badgePagamento, badgeTipo, brl, dataBR, dataISO, esc, resumo, toast } from "../dom.js";
import { estado, paginaAtual } from "../estado.js";
import { irPara, recarregar } from "../router.js";
import { FORMAS_PAGAMENTO, TIPOS } from "../types.js";
export async function verProcedimentos() {
    montarPagina({ titulo: "Procedimentos", descricao: "Consultas, vacinas, exames e cirurgias.", botao: "Agendar procedimento", aoClicar: () => void formProcedimento() });
    let lista;
    let animais;
    try {
        [lista, animais] = await Promise.all([api(`/procedimentos?${pagina(paginaAtual())}`), carregarAnimais()]);
    }
    catch (e) {
        painelErro(e);
        return;
    }
    if (voltouPagina(lista))
        return;
    if (lista.length === 0) {
        if (animais.length)
            painelVazio("Nenhum procedimento agendado", "Agende a primeira consulta, vacina ou exame.", "Agendar procedimento", () => void formProcedimento(undefined, animais));
        else
            painelVazio("Nenhum procedimento agendado", "Antes de agendar, cadastre o animal que vai ser atendido.", "Ir para animais", () => irPara("animais"));
        return;
    }
    const animalPorId = porId(animais);
    const mapa = porId(lista);
    const linhas = lista.map((p) => `
    <tr>
      <td>${dataBR(p.data)}</td>
      <td><strong>${esc(p.nome)}</strong><span class="sub">${esc(resumo(p.descricao))}</span></td>
      <td>${badgeTipo(p.tipo)}</td>
      <td>${esc(animalPorId.get(p.id_animal)?.nome ?? "—")}</td>
      <td>${badgePagamento(p.forma_pagamento)}</td>
      <td class="num">${p.preco != null ? brl(p.preco) : "—"}</td>
      <td><div class="actions">${botaoAcao("editar", p.id, "Editar")}${botaoAcao("excluir", p.id, "Excluir", true)}</div></td>
    </tr>`).join("");
    const com = (id, fn) => {
        const p = mapa.get(id);
        if (p)
            fn(p);
    };
    preencherPainel(tabela(["Data", "Procedimento", "Tipo", "Paciente", "Pagamento", { t: "Preço" }, ""], linhas) + paginador(lista.length), {
        editar: (id) => com(id, (p) => void formProcedimento(p, animais)),
        excluir: (id) => com(id, (p) => void excluirProcedimento(p)),
    });
}
export async function formProcedimento(proc, animais, idAnimal) {
    let lista = animais;
    try {
        lista ??= await carregarAnimais();
    }
    catch (e) {
        avisarErro(e);
        return;
    }
    if (lista.length === 0) {
        toast("Cadastre um animal antes de agendar um procedimento.", true);
        return;
    }
    abrirFormulario({
        titulo: proc ? "Editar procedimento" : "Agendar procedimento",
        valores: proc ? { ...proc } : { id_animal: idAnimal ?? "", data: dataISO() },
        botao: proc ? "Salvar alterações" : "Agendar",
        campos: [
            { nome: "id_animal", rotulo: "Paciente", tipo: "select", inteiro: true, larga: true, opcoes: lista.map((a) => ({ valor: a.id, rotulo: `${a.nome} (${a.especie})` })) },
            { nome: "tipo", rotulo: "Tipo", tipo: "select", opcoes: TIPOS.map((t) => ({ valor: t, rotulo: t })) },
            { nome: "data", rotulo: "Data", tipo: "date", min: proc ? undefined : dataISO() },
            { nome: "nome", rotulo: "Nome do procedimento", maxlength: 100, larga: true, placeholder: "V10, hemograma, consulta de rotina…" },
            { nome: "preco", rotulo: "Preço (R$)", tipo: "number", min: 0, step: 0.01, inputmode: "decimal" },
            { nome: "forma_pagamento", rotulo: "Forma de pagamento", tipo: "select", opcional: true, vazio: "Ainda não pago", opcoes: FORMAS_PAGAMENTO.map((f) => ({ valor: f, rotulo: f })) },
            { nome: "descricao", rotulo: "Descrição", tipo: "textarea", maxlength: 500, larga: true },
        ],
        enviar: async (dados) => {
            if (proc) {
                await api(`/procedimentos/${proc.id}`, { metodo: "PATCH", json: dados });
                toast("Procedimento atualizado.");
            }
            else {
                await api("/procedimentos", { metodo: "POST", json: dados });
                toast("Procedimento agendado.");
            }
            if (estado.view === "procedimentos")
                recarregar();
        },
    });
}
async function excluirProcedimento(proc) {
    const ok = await confirmar({
        titulo: `Excluir ${proc.nome}?`,
        texto: `O procedimento de ${dataBR(proc.data)} vai sair do histórico do animal. Não dá para desfazer.`,
        botao: "Excluir procedimento",
    });
    if (!ok)
        return;
    try {
        await api(`/procedimentos/${proc.id}`, { metodo: "DELETE" });
        toast("Procedimento excluído.");
        recarregar();
    }
    catch (e) {
        avisarErro(e);
    }
}
