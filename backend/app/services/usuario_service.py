from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario import Usuario, RolEnum
from app.schemas.usuario import UsuarioCreate
from app.auth.security import hash_password, verify_password


def get_usuario_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def registrar_usuario(db: Session, data: UsuarioCreate) -> Usuario:
    if get_usuario_por_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )
    nuevo = Usuario(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password),
        rol=RolEnum.paciente,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def autenticar_usuario(db: Session, email: str, password: str) -> Usuario | None:
    usuario = get_usuario_por_email(db, email)
    if not usuario or not verify_password(password, usuario.password_hash):
        return None
    return usuario