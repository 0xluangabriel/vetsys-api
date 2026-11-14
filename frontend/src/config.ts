/** Ajuste aqui se a API estiver em outro endereço ou se as rotas mudarem. */
export const CONFIG = {
  API_URL: "http://127.0.0.1:8000",
  /** Itens por página nas tabelas. */
  LIMITE: 10,
  /** Máximo aceito pela API em uma listagem. */
  LIMITE_MAXIMO: 100,
  ADMIN: {
    listar: "/admin/usuarios",
    promover: (id: number) => `/admin/funcionarios/${id}`,
    rebaixar: (id: number) => `/admin/usuarios/${id}`,
    vincular: (id: number) => `/admin/usuarios/${id}/tutor`,
    excluir: (id: number) => `/admin/usuarios/${id}`,
  },
} as const;
