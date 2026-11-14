from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import select

from app.config import ALGORITMO, MINUTOS_EXPIRACAO, SECRET_KEY
from app.database import SessionDep
from app.models import PerfilUsuario, Usuario

password_hash = PasswordHash.recommended()
hash_falso = password_hash.hash("abc123")
limiter = Limiter(key_func=get_remote_address)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def criar_token(email: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_EXPIRACAO)
    payload = {"sub": email, "exp": expira}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITMO)

def get_usuario_atual(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep) -> Usuario:
    erro = HTTPException(
        status_code=401,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
    except jwt.InvalidTokenError:
        raise erro
    email = payload.get("sub")
    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if usuario is None:
        raise erro
    return usuario

UsuarioAtual = Annotated[Usuario, Depends(get_usuario_atual)]

def get_funcionario(usuario: UsuarioAtual) -> Usuario:
    if usuario.perfil not in (PerfilUsuario.funcionario, PerfilUsuario.admin):
        raise HTTPException(status_code=403, detail="Acesso restrito a funcionários.")
    return usuario

FuncionarioAtual = Annotated[Usuario, Depends(get_funcionario)]

def get_tutor(usuario: UsuarioAtual) -> Usuario:
    if usuario.perfil != PerfilUsuario.tutor:
        raise HTTPException(status_code=403, detail="Acesso apenas para tutores.")
    if usuario.id_tutor is None:
        raise HTTPException(status_code=403, detail="Esse usuário não possui vínculo com tutor.")
    return usuario

TutorAtual = Annotated[Usuario, Depends(get_tutor)]

def get_admin(usuario: UsuarioAtual) -> Usuario:
    if usuario.perfil != PerfilUsuario.admin:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")
    return usuario

AdminAtual = Annotated[Usuario, Depends(get_admin)]
