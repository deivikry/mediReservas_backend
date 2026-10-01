from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import requiere_paciente, obtener_usuario_actual
from app.models.usuario import Usuario
from app.schemas.cita import CitaCreate, CitaOut
from app.services import cita_service

router = APIRouter(prefix="/citas", tags=["Citas"])


@router.post("/", response_model=CitaOut, status_code=status.HTTP_201_CREATED)
def crear(
    data: CitaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_paciente),
):
    return cita_service.crear_cita(db, usuario, data)


@router.get("/mis-citas", response_model=list[CitaOut])
def listar(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    return cita_service.listar_mis_citas(db, usuario)


@router.put("/{cita_id}/cancelar", response_model=CitaOut)
def cancelar(
    cita_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_paciente),
):
    return cita_service.cancelar_cita(db, usuario, cita_id)