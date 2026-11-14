/** Ajuste aqui se a API estiver em outro endereço ou se as rotas mudarem. */
export const CONFIG = {
    API_URL: "http://127.0.0.1:8000",
    /** Itens por página nas tabelas. */
    LIMITE: 10,
    /** Máximo aceito pela API em uma listagem. */
    LIMITE_MAXIMO: 100,
    ADMIN: {
        listar: "/admin/usuarios",
        promover: (id) => `/admin/funcionarios/${id}`,
        rebaixar: (id) => `/admin/usuarios/${id}`,
        vincular: (id) => `/admin/usuarios/${id}/tutor`,
        excluir: (id) => `/admin/usuarios/${id}`,
    },
};
