# VetSys Web

Interface web da [VetSys API](https://github.com/0xluangabriel/vetsys-api), escrita em **TypeScript sem framework**.

> Interface de demonstração gerada com auxílio de IA. O foco e a autoria do projeto estão na API.

## O que tem

- Login e cadastro, com tema claro e escuro
- Área da equipe: início com indicadores, tutores, animais (com ficha, carteira de vacinação e histórico) e procedimentos
- Área do administrador: liberar ou remover acesso, vincular uma conta a um tutor e excluir contas
- Área do tutor: os próprios animais e procedimentos, só para leitura
- O menu e as telas mudam conforme o perfil da conta

## Como rodar

1. Deixe a API rodando em `http://127.0.0.1:8000`, com o CORS liberado para `http://localhost:5500`.
2. Nesta pasta, sirva os arquivos:
   ```bash
   python -m http.server 5500
   ```
3. Abra **http://localhost:5500**.

O JavaScript compilado já está em `dist/`, então não é preciso instalar nada para usar.

## Como alterar o código

O código-fonte fica em `src/`. Depois de editar, recompile:

```bash
npm install     # só na primeira vez
npm run build   # ou: npm run dev, que recompila a cada alteração
```

## Estrutura

```
src/
├── main.ts          # entrada: login, sessão, tema e registro das telas
├── config.ts        # endereço da API e rotas de administração
├── types.ts         # tipos dos dados da API (Tutor, Animal, Procedimento...)
├── api.ts           # chamadas HTTP, token e tradução dos erros
├── estado.ts        # estado da sessão
├── router.ts        # menu lateral e troca de telas
├── componentes.ts   # tabela, paginação, formulário, confirmação e ficha
├── dom.ts           # utilitários: seleção, formatação, etiquetas e animações
├── dados.ts         # buscas de apoio (listas para os formulários)
├── icones.ts        # ícones em SVG
└── views/           # uma tela por arquivo
```

Se as rotas de administração da sua API tiverem outros caminhos, ajuste em `src/config.ts` e recompile.
