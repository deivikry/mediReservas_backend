from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import requiere_admin
from app.models.usuario import Usuario, RolEnum
from app.schemas.usuario import UsuarioOut
from fastapi import HTTPException, status

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/usuarios", response_model=list[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: Usuario = Depends(requiere_admin),
):
    return db.query(Usuario).all()


@router.put("/usuarios/{usuario_id}/rol", response_model=UsuarioOut)
def cambiar_rol(
    usuario_id: int,
    nuevo_rol: RolEnum,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requiere_admin),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    usuario.rol = nuevo_rol
    db.commit()
    db.refresh(usuario)
    return usuario