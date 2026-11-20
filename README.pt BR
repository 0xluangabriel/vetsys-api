# VetSys API

[English](README.md) | **Português**

[![Testes](https://github.com/0xluangabriel/vetsys-api/actions/workflows/testes.yml/badge.svg)](https://github.com/0xluangabriel/vetsys-api/actions/workflows/testes.yml)

API REST para gestão de clínicas veterinárias (tutores, animais, procedimentos, histórico clínico e carteira de vacinação), com autenticação JWT, controle de acesso por quatro perfis e um portal em que cada tutor vê apenas os próprios dados. Construída com Python, FastAPI, SQLModel e MySQL, com foco em segurança, testes automatizados e execução reproduzível com Docker.

É a evolução do **VetSys CLI**, um sistema de terminal com dados em JSON, reconstruído como API com banco relacional.

<div align="center">

**Vídeo de apresentação (narrado em inglês, cerca de 4 minutos)**

<a href="https://youtu.be/9KRZdcCzR4Q">
  <img src="https://img.youtube.com/vi/9KRZdcCzR4Q/hqdefault.jpg" alt="Vídeo de apresentação da VetSys API, em inglês" width="480">
</a>

</div>

## Destaques

- **Segurança por padrão:** senhas com Argon2, JWT de 30 minutos, rate limiting, proteção contra IDOR, timing attack e mass assignment.
- **Privilégio mínimo no banco:** a API usa um usuário MySQL que não consegue alterar a estrutura; comandos como `DROP TABLE` são recusados.
- **Portal do tutor:** as rotas `/meus` não recebem ID na URL; o tutor é identificado pelo token, então não há parâmetro para trocar e ver dados de outro cliente.
- **Um comando para subir tudo:** `docker compose up --build` cria o banco, os usuários, aplica as migrações e só então inicia a API e o painel web.
- **Migrações versionadas:** a estrutura do banco é controlada com Alembic, sem `create_all`.
- **Testes e CI:** cerca de 35 testes com pytest, em banco isolado por teste, executados no GitHub Actions a cada push e pull request.
- **Integridade em duas camadas:** chaves estrangeiras e `UNIQUE` no banco, mais validação com Pydantic na API.

## Tecnologias

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.13 |
| API | FastAPI, SQLModel (SQLAlchemy + Pydantic) |
| Banco de dados | MySQL 8.4 (PyMySQL) |
| Migrações | Alembic |
| Autenticação | JWT (PyJWT), OAuth2 Password Flow, Argon2 (pwdlib) |
| Rate limiting | slowapi |
| Testes | pytest, TestClient, SQLite em memória |
| Integração contínua | GitHub Actions |
| Contêineres | Docker e Docker Compose |
| Servidor do front-end | nginx |
| Ferramentas | uv, python-dotenv |

## Modelo de dados

```mermaid
erDiagram
    TUTOR ||--o{ ANIMAL : possui
    ANIMAL ||--o{ PROCEDIMENTO : recebe
    TUTOR |o--o| USUARIO : "vinculado a"

    TUTOR {
        int id PK
        string nome
        string email UK
        string telefone
        string endereco
        string numero
        string cep
        string complemento "opcional"
    }
    ANIMAL {
        int id PK
        int id_tutor FK
        string nome
        string especie
        string raca
        string sexo
        string idade
        float peso
    }
    PROCEDIMENTO {
        int id PK
        int id_animal FK
        string nome
        string descricao
        float preco
        enum tipo
        enum forma_pagamento "opcional"
        date data
    }
    USUARIO {
        int id PK
        int id_tutor FK "opcional, único"
        string nome
        string email UK
        string senha_hash
        enum perfil
    }
```

- **Exclusão em cascata:** `ON DELETE CASCADE` no banco e `cascade_delete` no SQLModel. Excluir um tutor remove seus animais e os procedimentos deles.
- **Vínculo de conta:** `usuario.id_tutor` é `UNIQUE` com `ON DELETE SET NULL`. Cada tutor tem no máximo uma conta, e excluir o tutor desfaz o vínculo sem apagar a conta.
- **Perfil restrito no banco:** `usuario.perfil` é um `ENUM('comum', 'funcionario', 'admin', 'tutor')`, então valores inválidos são recusados também pelo MySQL.
- **Modelos por papel:** cada entidade tem `Create` (cadastro), `Edit` (`PATCH`, campos opcionais), a tabela e `Out` (saída filtrada).

## Autenticação e perfis

1. `POST /auth/registro` gera o hash Argon2 da senha e cria o usuário com perfil **comum**.
2. `POST /auth/login` recebe e-mail e senha (formulário OAuth2) e devolve um JWT.
3. As demais requisições enviam `Authorization: Bearer <token>`.
4. Uma dependência decodifica o token, busca o usuário no banco e confere o perfil antes de executar a rota.

O token expira em 30 minutos e guarda apenas o e-mail (`sub`). O perfil é lido do banco a cada requisição, então promoções, rebaixamentos e exclusões valem na hora, mesmo com um token ainda válido.

| Perfil | Permissões |
| --- | --- |
| `comum` | Cadastro e login (perfil de toda conta nova) |
| `tutor` | Consultar os próprios animais e procedimentos (`/meus`) |
| `funcionario` | Todas as rotas de tutores, animais e procedimentos |
| `admin` | Tudo do funcionário, mais a gestão de usuários |

O perfil não faz parte do modelo de cadastro, então ninguém se registra como funcionário, tutor ou administrador. O primeiro administrador é definido direto no banco (veja [Como executar](#como-executar)).

### Portal do tutor

Um administrador vincula uma conta a um tutor (`PATCH /admin/usuarios/{id}/tutor`), e a conta passa a ter o perfil `tutor`. As rotas `/meus` usam o `id_tutor` do token, nunca um ID enviado na requisição. Um tutor sem vínculo recebe `403`.

## Rotas

Acesso: **Pública**, **Tutor**, **Func.** (funcionário ou admin) e **Admin**. As listagens aceitam `?skip=0&limit=10`, com `limit` entre 1 e 100. A documentação interativa fica em `/docs` (Swagger), com o botão **Authorize**.

| Grupo | Rotas | Acesso |
| --- | --- | --- |
| Autenticação | `POST /auth/registro`, `POST /auth/login` | Pública |
| Portal do tutor | `GET /meus/animais`, `GET /meus/procedimentos` | Tutor |
| Tutores | `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `PATCH /{id}`, `DELETE /{id}`, `GET /{id}/animais` em `/tutores` | Func. |
| Animais | `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `PATCH /{id}`, `DELETE /{id}`, `GET /{id}/procedimentos`, `GET /{id}/vacinas` em `/animais` | Func. |
| Procedimentos | `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `PATCH /{id}`, `DELETE /{id}` em `/procedimentos` | Func. |
| Administração | `GET /admin/usuarios`, `GET /admin/funcionarios`, `PATCH /admin/funcionarios/{id}` (promove), `PATCH /admin/usuarios/{id}` (rebaixa), `PATCH /admin/usuarios/{id}/tutor` (vincula), `DELETE /admin/usuarios/{id}` | Admin |

Regras de negócio relevantes:

- O `PUT` de procedimento exige data futura, e o `PATCH` permite corrigir procedimentos já realizados.
- O administrador não pode alterar o próprio perfil nem excluir a própria conta.
- Promover ou rebaixar um usuário desfaz o vínculo com o tutor.

## Validações e respostas de erro

A API valida a entrada com Pydantic: nomes de 1 a 100 caracteres, e-mail único e em formato válido, senha de 8 a 128 caracteres, telefone com até 11 dígitos, CEP com 8 dígitos, peso entre 0 e 500 kg, e tipo de procedimento e forma de pagamento como `Enum`.

| Status | Quando |
| --- | --- |
| `400` | Regra de negócio violada (ex.: admin alterando o próprio perfil) |
| `401` | Token ausente, inválido ou expirado; login incorreto |
| `403` | Usuário autenticado sem permissão |
| `404` | Recurso inexistente |
| `409` | E-mail já cadastrado ou tutor já vinculado a outra conta |
| `422` | Dados fora das regras de validação |
| `429` | Muitas tentativas em pouco tempo |

## Segurança

| Risco | Como a API trata |
| --- | --- |
| Senhas vazadas | Hash Argon2 com salt aleatório; o hash nunca é devolvido (`response_model`) |
| Token forjado | JWT assinado com chave de no mínimo 32 caracteres, algoritmo fixo na verificação e expiração curta |
| Enumeração de contas | Mesma mensagem para e-mail inexistente e senha errada |
| Timing attack | Com e-mail inexistente, a senha é verificada contra um hash falso, para a resposta demorar o mesmo tempo |
| Força bruta | 5 tentativas de login e 5 cadastros por minuto por IP, com resposta `429` |
| IDOR | O tutor é identificado pelo token, nunca por um ID da requisição |
| Mass assignment | Os modelos de entrada não incluem `perfil`, `id` nem campos sensíveis |
| SQL injection | Todas as consultas passam pelo ORM, com parâmetros separados do SQL |
| Configuração insegura | A API não sobe sem `DATABASE_URL` ou com `SECRET_KEY` curta (fail fast) |
| Abuso do banco | Usuário de aplicação sem `DROP`, `ALTER` nem `CREATE` (veja abaixo) |
| Perfil inválido no banco | Coluna `perfil` como `ENUM`, além da validação na API |
| Segredos expostos | `.env` fora do Git e da imagem Docker; `.env.example` só com valores de exemplo; `alembic.ini` sem credenciais |
| Contêiner comprometido | API executada com usuário sem privilégios (`USER vetsys`), e MySQL sem porta exposta |
| Banco desatualizado | A API só inicia depois que as migrações terminam com sucesso |
| Imagens imprevisíveis | Versões fixas (`python:3.13-slim`, `mysql:8.4`, `nginx:1.27-alpine`, uv), e dependências de desenvolvimento fora da imagem de produção |

Também há CORS restrito às origens do front-end.

### Privilégio mínimo no banco

O banco tem dois usuários de aplicação, com papéis separados:

| Usuário | Usado por | Permissões |
| --- | --- | --- |
| `vetsys_app` | API, em todas as requisições | `SELECT`, `INSERT`, `UPDATE` e `DELETE` em `vetsys.*` |
| `vetsys_migrator` | Serviço `migrate`, só na inicialização | Todas em `vetsys.*` |
| `root` | Ninguém no dia a dia; só a criação dos usuários e acesso de emergência | Total |

A API não consegue alterar a estrutura do banco. Mesmo com uma falha explorada, comandos como `DROP TABLE` são recusados:

```
ERROR 1142 (42000): DROP command denied to user 'vetsys_app'
```

Os usuários são criados pelo script `docker/criar-usuarios.sh`, montado em `/docker-entrypoint-initdb.d/`; a imagem oficial do MySQL o executa apenas na primeira inicialização do volume. Eles usam o host `'%'` porque as conexões vêm de outros contêineres, com endereços da rede interna. Como o MySQL não tem porta exposta, isso não abre o banco para fora.

## Arquitetura com Docker

O `docker-compose.yml` define quatro serviços:

| Serviço | Imagem | Função | Porta exposta |
| --- | --- | --- | --- |
| `db` | `mysql:8.4` | Banco de dados, com volume persistente | nenhuma |
| `migrate` | build do Dockerfile | Roda `alembic upgrade head` e termina | nenhuma |
| `api` | build do Dockerfile | FastAPI em modo produção (`fastapi run`) | 8000 |
| `web` | `nginx:1.27-alpine` | Serve a pasta `frontend/` (montada como somente leitura) | 5500 |

Ordem de inicialização, garantida por `depends_on`:

```
db (healthcheck: mysqladmin ping)
 └─► migrate (só começa quando o db está saudável)
      └─► api (só começa quando o migrate termina com código 0)
           └─► web
```

- O healthcheck evita que o `migrate` tente conectar enquanto o MySQL ainda está inicializando.
- A condição `service_completed_successfully` garante que a API nunca sobe com o banco desatualizado: se uma migração falhar, a API não inicia.
- Os serviços se comunicam por uma rede interna criada pelo Compose, em que cada um é encontrado pelo nome. Por isso, a `DATABASE_URL` dentro dos contêineres usa o host `db`, e não `localhost`.
- O MySQL não tem porta exposta: só os contêineres da própria rede conseguem acessá-lo.

**Imagem da API (`Dockerfile`):**

- Base `python:3.13-slim`, com o `uv` copiado da imagem oficial em versão fixa.
- Dependências instaladas com `uv sync --frozen --no-dev`: versões exatas do `uv.lock` e sem as dependências de desenvolvimento (o pytest fica fora da imagem).
- O `pyproject.toml` e o `uv.lock` são copiados antes do código, para aproveitar o cache de camadas: mudar o código não reinstala as dependências.
- Copia apenas `app/`, `alembic.ini` e `migrations/`.
- Roda com um usuário sem privilégios (`USER vetsys`), e não como root.
- O `.dockerignore` exclui `.env`, `.venv`, `.git`, `tests`, caches e bancos locais.

## Migrações com Alembic

A estrutura do banco é versionada com Alembic. A aplicação não usa mais `create_all`: toda criação ou alteração de tabela passa por uma migração versionada no Git.

**Configuração:**

- O `migrations/env.py` lê a `DATABASE_URL` do ambiente e define `target_metadata = SQLModel.metadata`, importando `app.models` para registrar as tabelas.
- O `%` da URL é escapado (`%%`), porque o leitor de configuração do Alembic o trata como caractere especial (senhas com `@` viram `%40` na URL).
- O `alembic.ini` não guarda nenhuma URL de banco.
- O molde `script.py.mako` importa `sqlmodel`, necessário para os tipos que o SQLModel gera.

**Migrações atuais:**

| Revisão | Descrição |
| --- | --- |
| `a9cab24a4503` | Schema inicial: tabelas `tutor`, `animal`, `procedimento` e `usuario`, com chaves estrangeiras (`CASCADE` e `SET NULL`) e enums |
| `68835c2b95a0` | Converte `usuario.perfil` de `VARCHAR(20)` para `ENUM('comum', 'funcionario', 'admin', 'tutor')`, restringindo os valores também no banco |

A segunda migração surgiu de uma divergência real detectada pelo `alembic check` entre os modelos e o banco existente.

**No Docker**, as migrações rodam automaticamente pelo serviço `migrate`, a cada `docker compose up`. Só as pendentes são aplicadas.

**Fluxo para alterar o banco:**

1. Altere o modelo em `app/models.py`.
2. Gere a migração: `uv run alembic revision --autogenerate -m "descricao da mudanca"`.
3. Revise o arquivo gerado em `migrations/versions/`: o autogenerate não detecta tudo (por exemplo, renomeações aparecem como remoção e criação).
4. Aplique: `uv run alembic upgrade head`.
5. Confira: `uv run alembic check` deve responder `No new upgrade operations detected.`
6. Faça o commit da migração junto com a mudança no modelo.

| Comando | Função |
| --- | --- |
| `alembic upgrade head` | Aplica todas as migrações pendentes |
| `alembic downgrade -1` | Desfaz a última migração |
| `alembic current` | Mostra a versão atual do banco |
| `alembic history` | Lista todas as migrações |
| `alembic check` | Compara os modelos com o banco e aponta diferenças |
| `alembic stamp head` | Marca o banco como atualizado sem executar nada (para bancos criados antes do Alembic) |

## Estrutura do projeto

```
vetsys-api/
├── .github/workflows/testes.yml   # CI: pytest a cada push e pull request
├── app/
│   ├── config.py                  # variáveis de ambiente, validadas na inicialização
│   ├── database.py                # engine, sessão e dependência SessionDep
│   ├── models.py                  # tabelas, modelos de entrada/saída e enums
│   ├── security.py                # hash, JWT, rate limiter e dependências de perfil
│   ├── main.py                    # app, CORS, handlers e routers
│   └── routers/                   # auth, admin, tutores, animais, procedimentos, meus
├── migrations/                    # Alembic
│   ├── env.py                     # lê a DATABASE_URL do ambiente e usa o SQLModel.metadata
│   ├── script.py.mako             # molde das migrações (com import sqlmodel)
│   └── versions/                  # histórico de migrações
├── docker/
│   └── criar-usuarios.sh          # cria os usuários do MySQL na primeira inicialização
├── frontend/                      # painel web
├── tests/                         # conftest e 7 arquivos de teste
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitattributes                 # força fim de linha LF nos scripts .sh
├── alembic.ini                    # sem URL de banco: ela vem só do ambiente
├── .env.example                   # modelo das variáveis de ambiente
├── pyproject.toml
└── uv.lock
```

Os imports seguem uma só direção, para evitar dependências circulares: `config → database → models → security → routers → main`.

## Testes

Cerca de 35 testes com pytest e o TestClient do FastAPI. Cada teste roda num SQLite em memória novo e isolado: a ordem de execução não importa e nenhum banco real é necessário.

O `conftest.py` prepara:

- um banco em memória com `StaticPool` (todas as conexões compartilham o mesmo banco) e `PRAGMA foreign_keys=ON`, para que `CASCADE` e `SET NULL` funcionem como no MySQL;
- um cliente de teste com `dependency_overrides`, que troca a sessão do MySQL pela do banco de teste;
- o rate limiter desligado por padrão e religado apenas no teste do `429`;
- fixtures que criam um usuário de cada perfil direto no banco e entregam o cabeçalho `Authorization: Bearer <token>` pronto: `headers_comum`, `headers_funcionario`, `headers_admin` e `headers_tutor` (esta também cria e vincula um tutor).

**Cobertura:**

- **Autenticação:** registro válido sem expor `senha_hash`; e-mail duplicado (`409`); senha curta e e-mail inválido (`422`); mass assignment (`"perfil": "admin"` no registro resulta em conta comum); login com `access_token` e `token_type: bearer`; senha errada e e-mail inexistente com a mesma resposta (`401`); rate limiting (6ª tentativa em um minuto resulta em `429`); token de usuário excluído (`401`); requisição sem token e com token inválido (`401`).
- **Permissões:** matriz de acesso por perfil nas rotas de tutores, administração e portal; tutor sem vínculo (`id_tutor` nulo) recebe `403`, cenário montado excluindo o tutor vinculado, o que também valida o `ON DELETE SET NULL`.
- **IDOR:** com dois tutores, cada um com animais e procedimentos, o tutor autenticado recebe apenas os próprios registros (o teste confere quantidade e conteúdo). O teste foi validado reintroduzindo um bug real, uma consulta sem `join` que gerava produto cartesiano e vazava procedimentos de todos os clientes: falhou com o bug e passou com a correção.
- **Administração:** listagem sem `senha_hash` em nenhum item; segundo vínculo ao mesmo tutor (`409`); admin tentando se rebaixar (`400`); fluxo vincular, rebaixar e vincular outra conta (`200`), provando que o rebaixamento libera o vínculo.
- **CRUD:** tutor sem complemento (`201`, complemento nulo); `PATCH` parcial preserva campos não enviados; exclusão de tutor remove animais e procedimentos (cascata); exclusão de animal remove procedimentos; data passada rejeitada no `POST` e no `PUT` (`422`); `PATCH` permitido em procedimento passado (`200`).

```bash
uv run pytest -v
```

## Integração contínua

O workflow `.github/workflows/testes.yml` roda a suíte de testes a cada push e pull request, em um `ubuntu-latest`, com `astral-sh/setup-uv` e Python 3.13.

- Não depende de MySQL: define `DATABASE_URL=sqlite://`.
- Usa uma `SECRET_KEY` falsa, exclusiva para testes. O arquivo do workflow é público, então a chave real nunca é usada no CI. Segredos reais, se necessários (deploy, por exemplo), iriam para os GitHub Secrets.

## Como executar

### Com Docker (recomendado)

**Pré-requisito:** Docker Desktop (no Windows, com WSL 2).

1. Clone o repositório:
   ```bash
   git clone https://github.com/0xluangabriel/vetsys-api.git
   cd vetsys-api
   ```
2. Crie o `.env` a partir do modelo:
   ```bash
   cp .env.example .env
   ```
3. Preencha as variáveis (use senhas fortes e diferentes entre si):

   | Variável | Descrição |
   | --- | --- |
   | `SECRET_KEY` | Chave que assina os tokens JWT. Mínimo de 32 caracteres. Gere com `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `DB_ROOT_PASSWORD` | Senha do `root` do MySQL do contêiner |
   | `DB_PASSWORD` | Senha do usuário `vetsys_app` (usado pela API) |
   | `DB_MIGRATOR_PASSWORD` | Senha do usuário `vetsys_migrator` (usado pelas migrações) |
   | `DATABASE_URL` | Usada só para rodar fora do Docker. Dentro dos contêineres, o Compose monta a URL com o host `db` |

4. Suba os serviços:
   ```bash
   docker compose up --build
   ```
   Na primeira execução, o Docker baixa as imagens, cria o banco, cria os usuários, aplica as migrações e só então inicia a API.
5. Acesse:
   - Documentação interativa da API: http://localhost:8000/docs
   - Painel web: http://localhost:5500
6. Crie o primeiro administrador. Registre um usuário pelo `POST /auth/registro` (no Swagger ou no painel) e promova-o:
   ```bash
   docker compose exec db mysql -u vetsys_app -p vetsys -e "UPDATE usuario SET perfil = 'admin' WHERE email = 'seu-email@exemplo.com';"
   ```
   A senha pedida é a `DB_PASSWORD`. Depois, faça login novamente para que o perfil novo seja aplicado.

**Comandos do dia a dia:**

| Ação | Comando |
| --- | --- |
| Subir em segundo plano | `docker compose up -d` |
| Subir após mudar código ou dependências | `docker compose up --build` |
| Ver os logs da API | `docker compose logs -f api` |
| Desligar (mantém os dados) | `docker compose down` |
| Desligar e apagar os dados | `docker compose down -v` |

**Solução de problemas:**

- **`Access denied` (erro 1045) ao entrar no MySQL:** as senhas do `.env` só são lidas na primeira criação do volume. Se foram alteradas depois, recrie o banco com `docker compose down -v` (isso apaga os dados).
- **Usuários `vetsys_app` ou `vetsys_migrator` não existem:** verifique se o `docker/criar-usuarios.sh` está com fim de linha LF e recrie o volume.
- **Porta 8000 ocupada:** desligue qualquer outra instância da API rodando fora do Docker.

### Sem Docker

**Pré-requisitos:** Python 3.13+, [uv](https://docs.astral.sh/uv/) e um servidor MySQL.

1. Clone o repositório e instale as dependências:
   ```bash
   git clone https://github.com/0xluangabriel/vetsys-api.git
   cd vetsys-api
   uv sync
   ```
2. Crie o banco e o usuário da aplicação, que precisa apenas de `SELECT`, `INSERT`, `UPDATE` e `DELETE`:
   ```sql
   CREATE DATABASE vetsys;
   CREATE USER 'vetsys_app'@'localhost' IDENTIFIED BY 'uma_senha_forte';
   GRANT SELECT, INSERT, UPDATE, DELETE ON vetsys.* TO 'vetsys_app'@'localhost';
   ```
3. Gere uma chave secreta e crie o `.env` na raiz:
   ```
   DATABASE_URL=mysql+pymysql://vetsys_app:uma_senha_forte@localhost:3306/vetsys
   SECRET_KEY=a_chave_gerada
   ```
   Caracteres especiais na senha precisam ser codificados na URL (`@` vira `%40`).
4. Crie as tabelas. Elas não são mais criadas automaticamente: rode as migrações com um usuário administrativo, porque o `vetsys_app` não tem permissão de alterar a estrutura. Exemplo no PowerShell:
   ```powershell
   $env:DATABASE_URL = "mysql+pymysql://usuario_admin:senha@localhost:3306/vetsys"
   uv run alembic upgrade head
   Remove-Item Env:DATABASE_URL
   ```
5. Suba a API e o painel web (em dois terminais separados):
   ```bash
   uv run fastapi dev app/main.py
   python -m http.server 5500 --directory frontend
   ```
   A documentação fica em `http://127.0.0.1:8000/docs`, e o painel em `http://localhost:5500` (a porta 5500 é a liberada no CORS).
6. Cadastre um usuário e promova-o a admin no banco:
   ```sql
   UPDATE usuario SET perfil = 'admin' WHERE email = 'seu-email@exemplo.com';
   ```

## Próximos passos

- [x] Módulos com `APIRouter`
- [x] Limite máximo de paginação
- [x] Rate limiting e proteção contra timing attack
- [x] Portal do tutor com proteção contra IDOR
- [x] Testes automatizados com pytest
- [x] Integração contínua com GitHub Actions
- [x] Docker e Docker Compose
- [x] Migrações com Alembic
- [x] Usuários do banco com privilégio mínimo, inclusive no Docker
- [ ] Criação do primeiro administrador por variáveis de ambiente
- [ ] Deploy

## Sobre o front-end

O painel web (`frontend/`) foi desenvolvido com apoio de IA. O foco do projeto, desenvolvido por mim, é o back-end: API, banco de dados, segurança, testes e infraestrutura.

---

Desenvolvido por **Luan Gabriel Alves da Silva** · [LinkedIn](https://linkedin.com/in/luan-gabriel-silva) · [GitHub](https://github.com/0xluangabriel)
