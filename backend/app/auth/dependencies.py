from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models.usuario import Usuario, RolEnum
from app.auth.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if not payload:
        raise credenciales_exception

    # Rechazar refresh tokens en endpoints que esperan access
    if payload.get("type") != "access":
        raise credenciales_exception

    usuario_id = payload.get("sub")
    if not usuario_id:
        raise credenciales_exception

    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    if not usuario:
        raise credenciales_exception
    return usuario


def requiere_rol(*roles: RolEnum):
    def verificador(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta acción",
            )
        return usuario
    return verificador


def requiere_medico(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    if usuario.rol != RolEnum.medico:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de médico",
        )
    return usuario


def requiere_admin(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    if usuario.rol != RolEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador",
        )
    return usuario


def requiere_paciente(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    if usuario.rol != RolEnum.paciente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de paciente",
        )
    return usuario