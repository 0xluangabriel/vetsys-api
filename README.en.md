# VetSys API

[Português](README.md) | **English**

[![Tests](https://github.com/0xluangabriel/vetsys-api/actions/workflows/testes.yml/badge.svg)](https://github.com/0xluangabriel/vetsys-api/actions/workflows/testes.yml)

A REST API for managing veterinary clinics (pet owners, animals, procedures, medical history and vaccination records), with JWT authentication, access control based on four roles, and a portal where each pet owner sees only their own data. Built with Python, FastAPI, SQLModel and MySQL, with a focus on security, automated testing and reproducible deployment with Docker.

It is the evolution of **VetSys CLI**, a command-line system that stored data in JSON, rebuilt as an API backed by a relational database.

> The code is written in Portuguese, so route paths, table names, field names and role names appear in Portuguese. Their meaning is explained wherever they first appear.

<div align="center">

**Presentation video (narrated in English, about 4 minutes)**

<a href="https://youtu.be/9KRZdcCzR4Q">
  <img src="https://img.youtube.com/vi/9KRZdcCzR4Q/hqdefault.jpg" alt="VetSys API presentation video, in English" width="480">
</a>

</div>

## Highlights

- **Secure by default:** Argon2 password hashing, 30-minute JWTs, rate limiting, and protection against IDOR, timing attacks and mass assignment.
- **Least privilege in the database:** the API connects with a MySQL user that cannot change the schema, so commands such as `DROP TABLE` are denied.
- **Pet owner portal:** the `/meus` ("my") routes take no ID in the URL. The owner is identified by the token, so there is no parameter to change in order to see another client's data.
- **One command to start everything:** `docker compose up --build` creates the database and its users, applies the migrations, and only then starts the API and the web dashboard.
- **Versioned migrations:** the database schema is managed with Alembic, not `create_all`.
- **Tests and CI:** 32 pytest tests, each running against its own isolated database, executed by GitHub Actions on every push and pull request.
- **Integrity in two layers:** foreign keys and `UNIQUE` constraints in the database, plus Pydantic validation in the API.

## Tech stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.13 |
| API | FastAPI, SQLModel (SQLAlchemy + Pydantic) |
| Database | MySQL 8.4 (PyMySQL) |
| Migrations | Alembic |
| Authentication | JWT (PyJWT), OAuth2 Password Flow, Argon2 (pwdlib) |
| Rate limiting | slowapi |
| Testing | pytest, TestClient, in-memory SQLite |
| Continuous integration | GitHub Actions |
| Containers | Docker and Docker Compose |
| Front-end server | nginx |
| Tooling | uv, python-dotenv |

## Data model

Entity names: `TUTOR` (pet owner), `ANIMAL`, `PROCEDIMENTO` (procedure) and `USUARIO` (user account).

```mermaid
erDiagram
    TUTOR ||--o{ ANIMAL : owns
    ANIMAL ||--o{ PROCEDIMENTO : receives
    TUTOR |o--o| USUARIO : "linked to"

    TUTOR {
        int id PK
        string nome
        string email UK
        string telefone
        string endereco
        string numero
        string cep
        string complemento "optional"
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
        enum forma_pagamento "optional"
        date data
    }
    USUARIO {
        int id PK
        int id_tutor FK "optional, unique"
        string nome
        string email UK
        string senha_hash
        enum perfil
    }
```

- **Cascade delete:** `ON DELETE CASCADE` in the database and `cascade_delete` in SQLModel. Deleting a pet owner removes their animals and those animals' procedures.
- **Account link:** `usuario.id_tutor` is `UNIQUE` with `ON DELETE SET NULL`. Each pet owner has at most one account, and deleting the owner removes the link without deleting the account.
- **Role restricted in the database:** `usuario.perfil` (the user's role) is an `ENUM('comum', 'funcionario', 'admin', 'tutor')`, so MySQL also rejects invalid values.
- **One model per purpose:** each entity has a `Create` model (input), an `Edit` model (`PATCH`, all fields optional), the table model, and an `Out` model (filtered output).

## Authentication and roles

1. `POST /auth/registro` (sign-up) hashes the password with Argon2 and creates the user with the **comum** (regular) role.
2. `POST /auth/login` receives the email and password (OAuth2 form) and returns a JWT.
3. Every other request sends `Authorization: Bearer <token>`.
4. A dependency decodes the token, loads the user from the database and checks their role before the route runs.

The token expires after 30 minutes and stores only the email (`sub`). The role is read from the database on every request, so promotions, demotions and deletions take effect immediately, even while a token is still valid.

| Role | Meaning | Permissions |
| --- | --- | --- |
| `comum` | Regular user | Sign-up and login (the role of every new account) |
| `tutor` | Pet owner | View their own animals and procedures (`/meus`) |
| `funcionario` | Staff member | All routes for pet owners, animals and procedures |
| `admin` | Administrator | Everything staff can do, plus user management |

The role is not part of the sign-up model, so nobody can register as staff, pet owner or administrator. The first administrator is set directly in the database (see [How to run](#how-to-run)).

### Pet owner portal

An administrator links an account to a pet owner (`PATCH /admin/usuarios/{id}/tutor`), and the account receives the `tutor` role. The `/meus` routes use the `id_tutor` from the authenticated user, never an ID sent in the request. A pet owner account without a link receives `403`.

## Routes

Access levels: **Public**, **Owner** (`tutor`), **Staff** (`funcionario` or `admin`) and **Admin**. List routes accept `?skip=0&limit=10`, with `limit` between 1 and 100. Interactive documentation is available at `/docs` (Swagger), with an **Authorize** button.

| Group | Routes | Access |
| --- | --- | --- |
| Authentication | `POST /auth/registro`, `POST /auth/login` | Public |
| Pet owner portal | `GET /meus/animais`, `GET /meus/procedimentos` | Owner |
| Pet owners | `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `PATCH /{id}`, `DELETE /{id}`, `GET /{id}/animais` under `/tutores` | Staff |
| Animals | `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `PATCH /{id}`, `DELETE /{id}`, `GET /{id}/procedimentos`, `GET /{id}/vacinas` (vaccines) under `/animais` | Staff |
| Procedures | `POST`, `GET`, `GET /{id}`, `PUT /{id}`, `PATCH /{id}`, `DELETE /{id}` under `/procedimentos` | Staff |
| Administration | `GET /admin/usuarios`, `GET /admin/funcionarios`, `PATCH /admin/funcionarios/{id}` (promote), `PATCH /admin/usuarios/{id}` (demote), `PATCH /admin/usuarios/{id}/tutor` (link to owner), `DELETE /admin/usuarios/{id}` | Admin |

Key business rules:

- `PUT` on a procedure requires a future date, while `PATCH` allows corrections to procedures that already happened.
- An administrator cannot change their own role or delete their own account.
- Promoting or demoting a user removes their link to a pet owner.

## Validation and error responses

Input is validated with Pydantic: names from 1 to 100 characters, unique and well-formed email, password from 8 to 128 characters, phone number with up to 11 digits, Brazilian postal code (CEP) with 8 digits, weight between 0 and 500 kg, and procedure type and payment method as `Enum` values.

| Status | When |
| --- | --- |
| `400` | A business rule was violated (e.g., an admin changing their own role) |
| `401` | Missing, invalid or expired token; wrong login credentials |
| `403` | Authenticated user without permission |
| `404` | Resource not found |
| `409` | Email already registered, or pet owner already linked to another account |
| `422` | Data outside the validation rules |
| `429` | Too many attempts in a short time |

## Security

| Risk | How the API handles it |
| --- | --- |
| Leaked passwords | Argon2 hashing with a random salt; the hash is never returned (`response_model`) |
| Forged tokens | JWT signed with a key of at least 32 characters, a fixed algorithm on verification, and short expiration |
| Account enumeration | Same message for an unknown email and a wrong password |
| Timing attacks | For an unknown email, the password is checked against a dummy hash, so the response takes the same time |
| Brute force | 5 login attempts and 5 sign-ups per minute per IP, answered with `429` |
| IDOR | The pet owner is identified by the token, never by an ID in the request |
| Mass assignment | Input models do not include `perfil`, `id` or other sensitive fields |
| SQL injection | All queries go through the ORM, with parameters kept separate from the SQL |
| Insecure configuration | The API refuses to start without `DATABASE_URL` or with a short `SECRET_KEY` (fail fast) |
| Database abuse | The application user has no `DROP`, `ALTER` or `CREATE` permission (see below) |
| Invalid role in the database | The `perfil` column is an `ENUM`, in addition to validation in the API |
| Exposed secrets | `.env` is excluded from Git and from the Docker image; `.env.example` holds only sample values; `alembic.ini` holds no credentials |
| Compromised container | The API runs as an unprivileged user (`USER vetsys`), and MySQL exposes no port |
| Outdated schema | The API only starts after the migrations finish successfully |
| Unpredictable images | Pinned versions (`python:3.13-slim`, `mysql:8.4`, `nginx:1.27-alpine`, uv), and development dependencies kept out of the production image |

CORS is also restricted to the front-end origins.

### Least privilege in the database

The database has two application users with separate roles:

| User | Used by | Permissions |
| --- | --- | --- |
| `vetsys_app` | The API, on every request | `SELECT`, `INSERT`, `UPDATE` and `DELETE` on `vetsys.*` |
| `vetsys_migrator` | The `migrate` service, only at startup | All privileges on `vetsys.*` |
| `root` | Nobody in daily use; only for creating the users and for emergency access | Full |

The API cannot change the database schema. Even if a flaw were exploited, commands such as `DROP TABLE` would be denied:

```
ERROR 1142 (42000): DROP command denied to user 'vetsys_app'
```

The users are created by the `docker/criar-usuarios.sh` script, mounted at `/docker-entrypoint-initdb.d/`. The official MySQL image runs it only the first time the volume is initialized. The users have the host `'%'` because connections come from other containers, with addresses on the internal network. Since MySQL exposes no port, this does not open the database to the outside.

## Docker architecture

`docker-compose.yml` defines four services:

| Service | Image | Purpose | Exposed port |
| --- | --- | --- | --- |
| `db` | `mysql:8.4` | Database, with a persistent volume | none |
| `migrate` | built from the Dockerfile | Runs `alembic upgrade head` and exits | none |
| `api` | built from the Dockerfile | FastAPI in production mode (`fastapi run`) | 8000 |
| `web` | `nginx:1.27-alpine` | Serves the `frontend/` folder (mounted read-only) | 5500 |

Startup order, enforced by `depends_on`:

```
db (healthcheck: mysqladmin ping)
 └─► migrate (starts only when db is healthy)
      └─► api (starts only when migrate exits with code 0)
           └─► web
```

- The healthcheck prevents `migrate` from trying to connect while MySQL is still starting up.
- The `service_completed_successfully` condition ensures the API never starts against an outdated schema: if a migration fails, the API does not start.
- The services communicate over an internal network created by Compose, where each one is reachable by its name. That is why the `DATABASE_URL` inside the containers uses the host `db` instead of `localhost`.
- MySQL exposes no port: only containers on the same network can reach it.

**API image (`Dockerfile`):**

- Based on `python:3.13-slim`, with `uv` copied from its official image at a pinned version.
- Dependencies installed with `uv sync --frozen --no-dev`: the exact versions from `uv.lock`, without development dependencies (pytest is left out of the image).
- `pyproject.toml` and `uv.lock` are copied before the code to take advantage of layer caching: changing the code does not reinstall the dependencies.
- Only `app/`, `alembic.ini` and `migrations/` are copied.
- Runs as an unprivileged user (`USER vetsys`), not as root.
- `.dockerignore` excludes `.env`, `.venv`, `.git`, `tests`, caches and local databases.

## Migrations with Alembic

The database schema is versioned with Alembic. The application no longer uses `create_all`: every table creation or change goes through a migration tracked in Git.

**Configuration:**

- `migrations/env.py` reads `DATABASE_URL` from the environment and sets `target_metadata = SQLModel.metadata`, importing `app.models` to register the tables.
- The `%` character in the URL is escaped as `%%`, because Alembic's configuration parser treats it as special (passwords containing `@` become `%40` in the URL).
- `alembic.ini` stores no database URL.
- The `script.py.mako` template imports `sqlmodel`, which is required for the types SQLModel generates.

**Current migrations:**

| Revision | Description |
| --- | --- |
| `a9cab24a4503` | Initial schema: tables `tutor`, `animal`, `procedimento` and `usuario`, with foreign keys (`CASCADE` and `SET NULL`) and enums |
| `68835c2b95a0` | Converts `usuario.perfil` from `VARCHAR(20)` to `ENUM('comum', 'funcionario', 'admin', 'tutor')`, restricting the values in the database as well |

The second migration came from a real mismatch between the models and the existing database, detected by `alembic check`.

**With Docker**, migrations run automatically through the `migrate` service on every `docker compose up`. Only pending migrations are applied.

**Workflow for changing the database:**

1. Change the model in `app/models.py`.
2. Generate the migration: `uv run alembic revision --autogenerate -m "description of the change"`.
3. Review the generated file in `migrations/versions/`. Autogenerate does not detect everything (for example, a rename appears as a drop followed by a create).
4. Apply it: `uv run alembic upgrade head`.
5. Verify: `uv run alembic check` should answer `No new upgrade operations detected.`
6. Commit the migration together with the model change.

| Command | What it does |
| --- | --- |
| `alembic upgrade head` | Applies all pending migrations |
| `alembic downgrade -1` | Reverts the last migration |
| `alembic current` | Shows the database's current revision |
| `alembic history` | Lists all migrations |
| `alembic check` | Compares the models with the database and reports differences |
| `alembic stamp head` | Marks the database as up to date without running anything (for databases created before Alembic) |

## Project structure

```
vetsys-api/
├── .github/workflows/testes.yml   # CI: runs pytest on every push and pull request
├── app/
│   ├── config.py                  # environment variables, validated at startup
│   ├── database.py                # engine, session and the SessionDep dependency
│   ├── models.py                  # tables, input/output models and enums
│   ├── security.py                # hashing, JWT, rate limiter and role dependencies
│   ├── main.py                    # app, CORS, handlers and routers
│   └── routers/                   # auth, admin, tutores, animais, procedimentos, meus
├── migrations/                    # Alembic
│   ├── env.py                     # reads DATABASE_URL from the environment and uses SQLModel.metadata
│   ├── script.py.mako             # migration template (with import sqlmodel)
│   └── versions/                  # migration history
├── docker/
│   └── criar-usuarios.sh          # creates the MySQL users on first startup
├── frontend/                      # web dashboard
├── tests/                         # conftest and 7 test files
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitattributes                 # forces LF line endings in .sh scripts
├── alembic.ini                    # no database URL: it comes only from the environment
├── .env.example                   # template for the environment variables
├── pyproject.toml
└── uv.lock
```

Imports flow in a single direction to avoid circular dependencies: `config → database → models → security → routers → main`.

## Tests

32 tests with pytest and FastAPI's TestClient. Each test runs against a fresh, isolated in-memory SQLite database, so execution order does not matter and no real database is needed.

| File | Tests | What it covers |
| --- | --- | --- |
| `test_auth.py` | 12 | Sign-up, login, mass assignment, rate limiting and tokens |
| `test_permissoes.py` | 7 | Access matrix by role and pet owner account without a link |
| `test_admin.py` | 4 | Listing without the hash, duplicate link, self-demotion and link release |
| `test_tutores.py` | 3 | Creation without `complemento`, partial `PATCH` and cascade delete |
| `test_procedimentos.py` | 3 | Past date on `POST` and `PUT`, and `PATCH` on a past procedure |
| `test_meus.py` | 2 | IDOR on animals and procedures |
| `test_animais.py` | 1 | Cascade delete of procedures |
| **Total** | **32** | |

`conftest.py` sets up:

- an in-memory database with `StaticPool` (all connections share the same database) and `PRAGMA foreign_keys=ON`, so that `CASCADE` and `SET NULL` behave as they do in MySQL;
- a test client with `dependency_overrides`, which replaces the MySQL session with the test database session;
- the rate limiter, disabled by default and re-enabled only in the `429` test;
- fixtures that create one user for each role directly in the database and return a ready-to-use `Authorization: Bearer <token>` header: `headers_comum`, `headers_funcionario`, `headers_admin` and `headers_tutor` (the last one also creates and links a pet owner).

**Coverage:**

- **Authentication:** valid sign-up without exposing `senha_hash` (the password hash); duplicate email (`409`); short password and invalid email (`422`); mass assignment (`"perfil": "admin"` in the sign-up body still creates a regular account); login returning `access_token` and `token_type: bearer`; wrong password and unknown email with the same response (`401`); rate limiting (the 6th attempt within a minute returns `429`); token of a deleted user (`401`); request with no token and with an invalid token (`401`).
- **Permissions:** an access matrix by role across the pet owner, administration and portal routes; a pet owner account without a link (`id_tutor` is null) receives `403`. The scenario is built by deleting the linked pet owner, which also validates `ON DELETE SET NULL`.
- **IDOR:** with two pet owners, each with animals and procedures, the authenticated owner receives only their own records (the test checks both the count and the content). The test was validated by reintroducing a real bug, a query without a `join` that produced a Cartesian product and leaked every client's procedures: it failed with the bug and passed with the fix.
- **Administration:** user listing without `senha_hash` in any item; a second link to the same pet owner (`409`); an admin trying to demote themselves (`400`); the flow of linking, demoting and then linking another account (`200`), which proves that demotion releases the link.
- **CRUD:** pet owner without the optional `complemento` field (`201`, stored as null); partial `PATCH` keeps the fields that were not sent; deleting a pet owner removes their animals and procedures (cascade); deleting an animal removes its procedures; past dates rejected on `POST` and `PUT` (`422`); `PATCH` allowed on a past procedure (`200`).

```bash
uv run pytest -v
```

## Continuous integration

The `.github/workflows/testes.yml` workflow runs the test suite on every push and pull request, on `ubuntu-latest`, with `astral-sh/setup-uv` and Python 3.13.

- It does not depend on MySQL: it sets `DATABASE_URL=sqlite://`.
- It uses a fake `SECRET_KEY` that exists only for testing. The workflow file is public, so the real key is never used in CI. Real secrets, if ever needed (for deployment, for example), would go into GitHub Secrets.

## How to run

### With Docker (recommended)

**Prerequisite:** Docker Desktop (on Windows, with WSL 2).

1. Clone the repository:
   ```bash
   git clone https://github.com/0xluangabriel/vetsys-api.git
   cd vetsys-api
   ```
2. Create the `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
3. Fill in the variables (use strong passwords, each one different):

   | Variable | Description |
   | --- | --- |
   | `SECRET_KEY` | Key used to sign the JWTs. At least 32 characters. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `DB_ROOT_PASSWORD` | Password for the MySQL `root` user in the container |
   | `DB_PASSWORD` | Password for the `vetsys_app` user (used by the API) |
   | `DB_MIGRATOR_PASSWORD` | Password for the `vetsys_migrator` user (used by the migrations) |
   | `DATABASE_URL` | Used only when running without Docker. Inside the containers, Compose builds the URL with the host `db` |

4. Start the services:
   ```bash
   docker compose up --build
   ```
   On the first run, Docker downloads the images, creates the database and its users, applies the migrations, and only then starts the API.
5. Open:
   - Interactive API documentation: http://localhost:8000/docs
   - Web dashboard: http://localhost:5500
6. Create the first administrator. Register a user through `POST /auth/registro` (in Swagger or in the dashboard) and promote it:
   ```bash
   docker compose exec db mysql -u vetsys_app -p vetsys -e "UPDATE usuario SET perfil = 'admin' WHERE email = 'your-email@example.com';"
   ```
   When asked for a password, enter `DB_PASSWORD`. Then log in again so the new role takes effect.

**Everyday commands:**

| Action | Command |
| --- | --- |
| Start in the background | `docker compose up -d` |
| Start after changing code or dependencies | `docker compose up --build` |
| Follow the API logs | `docker compose logs -f api` |
| Stop (keeps the data) | `docker compose down` |
| Stop and delete the data | `docker compose down -v` |

**Troubleshooting:**

- **`Access denied` (error 1045) when connecting to MySQL:** the passwords in `.env` are only read when the volume is first created. If you changed them afterwards, recreate the database with `docker compose down -v` (this deletes the data).
- **The `vetsys_app` or `vetsys_migrator` user does not exist:** make sure `docker/criar-usuarios.sh` uses LF line endings, then recreate the volume.
- **Port 8000 is already in use:** stop any other instance of the API running outside Docker.

### Without Docker

**Prerequisites:** Python 3.13+, [uv](https://docs.astral.sh/uv/) and a MySQL server.

1. Clone the repository and install the dependencies:
   ```bash
   git clone https://github.com/0xluangabriel/vetsys-api.git
   cd vetsys-api
   uv sync
   ```
2. Create the database and the application user, which needs only `SELECT`, `INSERT`, `UPDATE` and `DELETE`:
   ```sql
   CREATE DATABASE vetsys;
   CREATE USER 'vetsys_app'@'localhost' IDENTIFIED BY 'a_strong_password';
   GRANT SELECT, INSERT, UPDATE, DELETE ON vetsys.* TO 'vetsys_app'@'localhost';
   ```
3. Generate a secret key and create a `.env` file in the project root:
   ```
   DATABASE_URL=mysql+pymysql://vetsys_app:a_strong_password@localhost:3306/vetsys
   SECRET_KEY=the_generated_key
   ```
   Special characters in the password must be URL-encoded (`@` becomes `%40`).
4. Create the tables. They are no longer created automatically: run the migrations with an administrative user, because `vetsys_app` is not allowed to change the schema. Example in PowerShell:
   ```powershell
   $env:DATABASE_URL = "mysql+pymysql://admin_user:password@localhost:3306/vetsys"
   uv run alembic upgrade head
   Remove-Item Env:DATABASE_URL
   ```
5. Start the API and the web dashboard (in two separate terminals):
   ```bash
   uv run fastapi dev app/main.py
   python -m http.server 5500 --directory frontend
   ```
   The documentation is at `http://127.0.0.1:8000/docs`, and the dashboard at `http://localhost:5500` (port 5500 is the one allowed by CORS).
6. Register a user and promote it to admin in the database:
   ```sql
   UPDATE usuario SET perfil = 'admin' WHERE email = 'your-email@example.com';
   ```

## Roadmap

- [x] Modular routes with `APIRouter`
- [x] Maximum pagination limit
- [x] Rate limiting and timing-attack protection
- [x] Pet owner portal with IDOR protection
- [x] Automated tests with pytest
- [x] Continuous integration with GitHub Actions
- [x] Docker and Docker Compose
- [x] Migrations with Alembic
- [x] Least-privilege database users, including in Docker

## About the front-end

The web dashboard (`frontend/`) was built with the help of AI. The focus of this project, developed by me, is the back end: the API, database, security, tests and infrastructure.

---

Developed by **Luan Gabriel Alves da Silva** · [LinkedIn](https://linkedin.com/in/luan-gabriel-silva) · [GitHub](https://github.com/0xluangabriel)
