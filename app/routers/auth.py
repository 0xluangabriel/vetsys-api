from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import SessionDep
from app.models import Usuario, UsuarioCreate, UsuarioOut
from app.security import criar_token, hash_falso, limiter, password_hash

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/registro", status_code=201, response_model=UsuarioOut)
def registrar(dados: UsuarioCreate, session: SessionDep):
    usuario = Usuario(nome=dados.nome, email=dados.email, senha_hash=password_hash.hash(dados.senha))
    session.add(usuario)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    session.refresh(usuario)
    return usuario

@router.post("/login")
@limiter.limit("5/minute")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep, request: Request):
    usuario = session.exec(select(Usuario).where(Usuario.email == form.username)).first()
    if usuario is None:
        password_hash.verify(form.password, hash_falso)
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    if not password_hash.verify(form.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    return {"access_token": criar_token(usuario.email), "token_type": "bearer"}