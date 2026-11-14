from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import SessionDep
from app.models import Usuario, Tutor, PerfilUsuario, UsuarioAdminOut, TutorUserEdit
from app.security import AdminAtual

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/funcionarios", response_model=list[UsuarioAdminOut])
def listar_funcionarios(session: SessionDep, usuario: AdminAtual, skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100)):
    return session.exec(select(Usuario).order_by(Usuario.id).where(Usuario.perfil == PerfilUsuario.funcionario).offset(skip).limit(limit)).all()

@router.get("/usuarios", response_model=list[UsuarioAdminOut])
def listar_usuarios(session: SessionDep, usuario: AdminAtual, skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100)):
    return session.exec(select(Usuario).order_by(Usuario.id).offset(skip).limit(limit)).all()

@router.patch("/funcionarios/{id_usuario}", response_model=UsuarioAdminOut)
def definir_funcionario(id_usuario: int, session: SessionDep, usuario: AdminAtual):
    alvo = session.get(Usuario, id_usuario)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == usuario.id:
        raise HTTPException(status_code=400, detail="Você não pode se rebaixar de admin.")
    alvo.perfil = PerfilUsuario.funcionario
    alvo.id_tutor = None
    session.add(alvo)
    session.commit()
    session.refresh(alvo)
    return alvo

@router.patch("/usuarios/{id_usuario}", response_model=UsuarioAdminOut)
def definir_comum(id_usuario: int, session: SessionDep, usuario: AdminAtual):
    alvo = session.get(Usuario, id_usuario)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == usuario.id:
        raise HTTPException(status_code=400, detail="Você não pode se rebaixar de admin.")
    alvo.perfil = PerfilUsuario.comum
    alvo.id_tutor = None
    session.add(alvo)
    session.commit()
    session.refresh(alvo)
    return alvo

@router.patch("/usuarios/{id_usuario}/tutor", response_model=UsuarioAdminOut)
def definir_tutor(id_usuario: int, session: SessionDep, dados: TutorUserEdit, usuario: AdminAtual):
    alvo = session.get(Usuario, id_usuario)
    tutor = session.get(Tutor, dados.id_tutor)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == usuario.id:
        raise HTTPException(status_code=400, detail="Você não pode se rebaixar de admin.")
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor não encontrado.")
    alvo.perfil = PerfilUsuario.tutor
    alvo.id_tutor = dados.id_tutor
    session.add(alvo)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Tutor já vinculado a um usuário.")
    session.refresh(alvo)
    return alvo

@router.delete("/usuarios/{id_usuario}")
def excluir_usuario(id_usuario: int, session: SessionDep, usuario: AdminAtual):
    alvo = session.get(Usuario, id_usuario)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == usuario.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir a si mesmo.")
    session.delete(alvo)
    session.commit()
    return {"mensagem": "Usuário excluído com sucesso."}
