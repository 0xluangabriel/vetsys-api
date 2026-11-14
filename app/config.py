import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError('Sua DATABASE_URL não está no .env.')

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError('Sua SECRET KEY não está no .env, gere uma com python -c "import secrets; print(secrets.token_hex(32))".')
elif len(SECRET_KEY) < 32:
    raise RuntimeError('Sua SECRET KEY tem menos de 32 caracteres, gere uma com python -c "import secrets; print(secrets.token_hex(32))".')

ALGORITMO = "HS256"
MINUTOS_EXPIRACAO = 30