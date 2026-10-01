from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioOut, Token, RefreshRequest
from app.services.usuario_service import registrar_usuario, autenticar_usuario
from app.auth.security import create_access_token, create_refresh_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registro(data: UsuarioCreate, db: Session = Depends(get_db)):
    return registrar_usuario(db, data)


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, form.username, form.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = {"sub": str(usuario.id), "rol": usuario.rol.value}
    return Token(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
    )


@router.post("/refresh", response_model=Token)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_access_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    nuevo_payload = {"sub": payload.get("sub"), "rol": payload.get("rol")}
    return Token(
        access_token=create_access_token(nuevo_payload),
        refresh_token=create_refresh_token(nuevo_payload),
    )