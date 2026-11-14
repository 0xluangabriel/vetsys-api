import { painelErro } from "../componentes.js";
import { carregarAnimais, carregarProcedimentos, carregarTutores, porId } from "../dados.js";
import { $, $$, badgeTipo, classeTipo, contarAte, dataISO, diaMes, emCascata, esc, esqueleto } from "../dom.js";
import { estado } from "../estado.js";
import { ICONES, PATA } from "../icones.js";
import { irPara } from "../router.js";
import { FORMAS_PAGAMENTO, TIPOS } from "../types.js";
import { CONFIG } from "../config.js";
export async function verInicio() {
    const conteudo = $("#conteudo");
    const nome = estado.email.split("@")[0] ?? "";
    const hoje = new Intl.DateTimeFormat("pt-BR", { weekday: "long", day: "numeric", month: "long" }).format(new Date());
    conteudo.innerHTML = `
    <section class="hero">${PATA.replace("<svg", '<svg class="paws"')}
      <h1>Olá, ${esc(nome)}</h1>
      <p>${esc(hoje.charAt(0).toUpperCase() + hoje.slice(1))}. Veja o que vem pela frente na clínica.</p>
    </section>
    <div id="painel">${esqueleto(4)}</div>`;
    let tutores, animais, procs;
    try {
        [tutores, animais, procs] = await Promise.all([carregarTutores(), carregarAnimais(), carregarProcedimentos()]);
    }
    catch (e) {
        painelErro(e);
        return;
    }
    const hojeISO = dataISO();
    const em30 = new Date();
    em30.setDate(em30.getDate() + 30);
    const limite30 = dataISO(em30);
    const futuros = procs.filter((p) => p.data >= hojeISO).sort((a, b) => a.data.localeCompare(b.data));
    const vacinas30 = futuros.filter((p) => p.tipo === "Vacinação" && p.data <= limite30);
    const pendentes = procs.filter((p) => !p.forma_pagamento);
    const animalPorId = porId(animais);
    const cheio = (n) => (n >= CONFIG.LIMITE_MAXIMO ? "+" : "");
    const stat = (icone, valor, sufixo, rotulo, view, destaque = false) => `<button type="button" class="stat${destaque ? " destaque" : ""}" data-ir="${view}"><span class="ico">${icone}</span><strong data-num="${valor}" data-sufixo="${sufixo}">0</strong><span>${rotulo}</span></button>`;
    const agenda = futuros.slice(0, 6).map((p) => {
        const { dia, mes } = diaMes(p.data);
        const animal = animalPorId.get(p.id_animal);
        return `<li><span class="dia"><b>${dia}</b><small>${mes}</small></span>
      <div class="info"><strong>${esc(p.nome)}</strong><span>${esc(animal?.nome ?? "Paciente")}${animal ? `, ${esc(animal.especie)}` : ""}</span></div>
      ${badgeTipo(p.tipo)}</li>`;
    }).join("");
    const barras = (itens) => {
        const maior = Math.max(1, ...itens.map((i) => i.n));
        return `<ul class="barras">${itens.map((i) => `<li><div class="rot"><span>${esc(i.rotulo)}</span><b>${i.n}</b></div><div class="trilho"><i class="${i.classe}" style="--w:${(i.n / maior) * 100}%"></i></div></li>`).join("")}</ul>`;
    };
    const porTipo = TIPOS.map((t) => ({ rotulo: t, n: procs.filter((p) => p.tipo === t).length, classe: classeTipo(t) }));
    const porPagamento = [
        ...FORMAS_PAGAMENTO.map((f) => ({ rotulo: f, n: procs.filter((p) => p.forma_pagamento === f).length, classe: "pg-pago" })),
        { rotulo: "Pendente", n: pendentes.length, classe: "pg-pendente" },
    ];
    const painel = $("#painel");
    painel.innerHTML = `
    <div class="stats">
      ${stat(ICONES.tutores, tutores.length, cheio(tutores.length), "tutores cadastrados", "tutores")}
      ${stat(PATA, animais.length, cheio(animais.length), "pacientes", "animais")}
      ${stat(ICONES.agenda, futuros.length, "", "procedimentos agendados", "procedimentos")}
      ${stat(ICONES.vacina, vacinas30.length, "", "vacinas nos próximos 30 dias", "procedimentos", true)}
    </div>
    <div class="duas">
      <section class="bloco">
        <h2>Próximos atendimentos</h2>
        ${agenda ? `<ol class="agenda">${agenda}</ol>` : `<p class="vazio-curto">Nada agendado. Agende um procedimento para ele aparecer aqui.</p>`}
      </section>
      <div class="pilha">
        <section class="bloco">
          <h2>Procedimentos por tipo</h2>
          ${procs.length ? barras(porTipo) : `<p class="vazio-curto">Ainda não há procedimentos registrados.</p>`}
        </section>
        <section class="bloco">
          <h2>Pagamentos</h2>
          ${procs.length ? barras(porPagamento) : `<p class="vazio-curto">Os pagamentos aparecem aqui quando houver procedimentos.</p>`}
        </section>
      </div>
    </div>`;
    emCascata(painel, ".stat");
    emCascata(painel, ".agenda li");
    $$("[data-num]", painel).forEach((el) => contarAte(el, Number(el.dataset["num"]), el.dataset["sufixo"] ?? ""));
    $$("[data-ir]", painel).forEach((b) => b.addEventListener("click", () => irPara(b.dataset["ir"])));
}
