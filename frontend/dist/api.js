import { CONFIG } from "./config.js";
import { estado } from "./estado.js";
export class ApiError extends Error {
    status;
    constructor(status, mensagem) {
        super(mensagem);
        this.status = status;
        this.name = "ApiError";
    }
}
const ROTULOS = {
    nome: "Nome", email: "E-mail", telefone: "Telefone", senha: "Senha", especie: "Espécie",
    raca: "Raça", sexo: "Sexo", idade: "Idade", peso: "Peso", id_tutor: "Tutor",
    id_animal: "Paciente", descricao: "Descrição", preco: "Preço", tipo: "Tipo", data: "Data",
    endereco: "Endereço", numero: "Número", complemento: "Complemento", cep: "CEP",
    forma_pagamento: "Forma de pagamento", username: "E-mail", password: "Senha",
};
/** Transforma o corpo de erro da API numa frase para o usuário. */
function textoErro(corpo, status) {
    const detalhe = corpo?.detail;
    if (typeof detalhe === "string")
        return detalhe;
    if (Array.isArray(detalhe)) {
        return detalhe
            .map((e) => {
            const campo = String(e.loc?.[e.loc.length - 1] ?? "");
            const msg = String(e.msg ?? "").replace(/^Value error, /, "");
            return ROTULOS[campo] ? `${ROTULOS[campo]}: ${msg}` : msg;
        })
            .join("; ");
    }
    if (status === 403)
        return "Você não tem permissão para esta ação.";
    if (status === 429)
        return "Muitas tentativas. Aguarde um minuto e tente de novo.";
    return `A API respondeu com erro ${status}.`;
}
let aoExpirar = () => { };
/** Define o que fazer quando a API responde 401 numa rota protegida. */
export function aoExpirarSessao(fn) {
    aoExpirar = fn;
}
export async function api(caminho, opcoes = {}) {
    const headers = {};
    let body;
    if (opcoes.form) {
        headers["Content-Type"] = "application/x-www-form-urlencoded";
        body = new URLSearchParams(opcoes.form);
    }
    else if (opcoes.json !== undefined) {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(opcoes.json);
    }
    if (estado.token)
        headers["Authorization"] = `Bearer ${estado.token}`;
    let resposta;
    try {
        resposta = await fetch(CONFIG.API_URL + caminho, { method: opcoes.metodo ?? "GET", headers, body });
    }
    catch {
        throw new ApiError(0, `Não foi possível falar com a API em ${CONFIG.API_URL}. Confira se ela está rodando e se o CORS está liberado.`);
    }
    if (resposta.status === 204)
        return null;
    let corpo = null;
    try {
        corpo = await resposta.json();
    }
    catch {
        /* resposta sem corpo */
    }
    if (!resposta.ok) {
        if (resposta.status === 401 && !opcoes.publica)
            aoExpirar();
        throw new ApiError(resposta.status, textoErro(corpo, resposta.status));
    }
    return corpo;
}
/** Lê o e-mail (campo "sub") de dentro do token JWT, sem validar a assinatura. */
export function emailDoToken(token) {
    try {
        const parte = token.split(".")[1] ?? "";
        const base64 = parte.replace(/-/g, "+").replace(/_/g, "/");
        const bytes = Uint8Array.from(atob(base64), (c) => c.charCodeAt(0));
        const dados = JSON.parse(new TextDecoder().decode(bytes));
        return dados.sub ?? "";
    }
    catch {
        return "";
    }
}
export const ehErroApi = (e) => e instanceof ApiError;
export function mensagemDe(e) {
    return e instanceof Error ? e.message : "Erro inesperado.";
}
