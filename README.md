# VetSys API
![Testes](https://github.com/0xluangabriel/vetsys-api/actions/workflows/testes.yml/badge.svg)

API REST para gestão de clínicas veterinárias (tutores, animais, procedimentos, histórico clínico e carteira de vacinação), com autenticação JWT, controle de acesso por quatro perfis e um portal em que cada tutor vê apenas os próprios dados. Construída com Python, FastAPI, SQLModel e MySQL, com foco em segurança e em testes automatizados.

É a evolução do **VetSys CLI**, um sistema de terminal com dados em JSON, reconstruído como API com banco relacional.

<div align="center">

**Vídeo de apresentação (narrado em inglês, cerca de 4 minutos)**

<a href="https://youtu.be/9KRZdcCzR4Q">
  <img src="https://img.youtube.com/vi/9KRZdcCzR4Q/hqdefault.jpg" alt="Vídeo de apresentação da VetSys API, em inglês" width="480">
</a>

</div>

## Destaques

- **Segurança por padrão:** senhas com Argon2, JWT de 30 minutos, rate limiting, proteção contra IDOR, timing attack e mass assignment, e usuário de banco com privilégio mínimo.
- **Portal do tutor:** as rotas `/meus` não recebem ID na URL; o tutor é identificado pelo token, então não há parâmetro para trocar e ver dados de outro cliente.
- **Testes isolados:** cada teste roda em um banco SQLite em memória novo, com fixtures de autenticação por perfil.
- **Integridade em duas camadas:** chaves estrangeiras e `UNIQUE` no banco, mais validação com Pydantic na API.

## Tecnologias

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.13 |
| API | FastAPI, SQLModel (SQLAlchemy + Pydantic) |
| Banco de dados | MySQL (PyMySQL) |
| Autenticação | JWT (PyJWT), OAuth2 Password Flow, Argon2 (pwdlib) |
| Rate limiting | slowapi |
| Testes | pytest, TestClient, SQLite em memória |
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

O perfil não faz parte do modelo de cadastro, então ninguém se registra como funcionário, tutor ou administrador. O primeiro administrador é definido direto no banco:

```sql
UPDATE usuario SET perfil = 'admin' WHERE email = 'seu-email@exemplo.com';
```

### Portal do tutor

Um administrador vincula uma conta a um tutor (`PATCH /admin/usuarios/{id}/tutor`), e a conta passa a ter o perfil `tutor`. As rotas `/meus` usam o `id_tutor` do token, nunca um ID enviado na requisição.

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
| Abuso do banco | Usuário MySQL próprio, sem `DROP`, `ALTER` nem acesso a outros bancos |

Também há CORS restrito às origens do front-end e segredos fora do repositório, no `.env`.

## Estrutura do projeto

```
vetsys-api/
├── app/
│   ├── config.py          # variáveis de ambiente e validação na inicialização
│   ├── database.py        # engine, sessão e dependência SessionDep
│   ├── models.py          # tabelas, modelos de entrada/saída e enums
│   ├── security.py        # hash, JWT, rate limiter e dependências de perfil
│   ├── main.py            # app, CORS, handlers e routers
│   └── routers/           # auth, admin, tutores, animais, procedimentos, meus
├── tests/
│   ├── conftest.py        # banco em memória, cliente de teste e fixtures por perfil
│   ├── test_auth.py
│   └── test_permissoes.py
└── pyproject.toml
```

Os imports seguem uma só direção, para evitar dependências circulares: `config → database → models → security → routers → main`.

## Testes

Os testes usam pytest e o TestClient do FastAPI. Cada teste roda em um SQLite em memória novo, então a ordem de execução não importa e o banco de desenvolvimento nunca é tocado. O `conftest.py` prepara:

- um banco com `StaticPool` e `PRAGMA foreign_keys=ON`, para a cascata e o `SET NULL` funcionarem como no MySQL;
- `dependency_overrides`, que troca a sessão do MySQL pela do banco de teste;
- o rate limiter desligado por padrão e religado só no teste específico;
- fixtures que entregam o cabeçalho de autenticação pronto para cada perfil.

**Cobertura atual:** autenticação (registro sem vazar `senha_hash`, e-mail repetido, senha curta, mass assignment, login correto e incorreto, mesma mensagem para e-mail inexistente, rate limiting e token de usuário excluído) e permissões por perfil nas rotas protegidas.

```bash
uv run pytest -v
```

## Como executar

**Pré-requisitos:** Python 3.13+, [uv](https://docs.astral.sh/uv/) e um servidor MySQL.

1. Clone o repositório e instale as dependências:
   ```bash
   git clone https://github.com/0xluangabriel/vetsys-api.git
   cd vetsys-api
   uv sync
   ```
2. Crie o banco e um usuário com privilégio mínimo:
   ```sql
   CREATE DATABASE vetsys;
   CREATE USER 'vetsys_app'@'localhost' IDENTIFIED BY 'uma_senha_forte';
   GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, REFERENCES
       ON vetsys.* TO 'vetsys_app'@'localhost';
   ```
3. Gere uma chave secreta com `python -c "import secrets; print(secrets.token_hex(32))"` e crie o `.env` na raiz:
   ```
   DATABASE_URL=mysql+pymysql://vetsys_app:uma_senha_forte@localhost:3306/vetsys
   SECRET_KEY=a_chave_gerada
   ```
   Caracteres especiais na senha precisam ser codificados na URL (`@` vira `%40`).
4. Inicie a API com `uv run fastapi dev app/main.py` e acesse `http://127.0.0.1:8000/docs`. Cadastre um usuário e promova-o a admin no banco (veja [Autenticação e perfis](#autenticação-e-perfis)).

As tabelas são criadas automaticamente na primeira execução.

## Próximos passos

- [x] Módulos com `APIRouter`
- [x] Limite máximo de paginação
- [x] Rate limiting e proteção contra timing attack
- [x] Portal do tutor com proteção contra IDOR
- [x] Ampliar os testes (tutores, animais e procedimentos)
- [x] Integração contínua com GitHub Actions
- [ ] Docker e docker-compose
- [ ] Migrations com Alembic
- [ ] Deploy

---

Desenvolvido por **Luan Gabriel Alves da Silva** · [LinkedIn](https://linkedin.com/in/luan-gabriel-silva) · [GitHub](https://github.com/0xluangabriel)
