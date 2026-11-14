export const estado = {
    token: null,
    email: "",
    papel: "equipe",
    admin: false,
    view: "",
    pagina: {},
};
export function paginaAtual(view = estado.view) {
    return estado.pagina[view] ?? 0;
}
export function guardar(chave, valor) {
    try {
        if (valor === null)
            sessionStorage.removeItem(chave);
        else
            sessionStorage.setItem(chave, valor);
    }
    catch {
        /* navegador sem armazenamento: a sessão dura até fechar a aba */
    }
}
export function lerGuardado(chave) {
    try {
        return sessionStorage.getItem(chave);
    }
    catch {
        return null;
    }
}
