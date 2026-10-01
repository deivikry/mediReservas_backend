from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import requiere_medico
from app.models.usuario import Usuario
from app.schemas.horario import HorarioCreate, HorarioUpdate, HorarioOut
from app.services import horario_service

router = APIRouter(prefix="/horarios", tags=["Horarios"])


@router.post("/", response_model=HorarioOut, status_code=status.HTTP_201_CREATED)
def crear(
    data: HorarioCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_medico),
):
    return horario_service.crear_horario(db, usuario, data)


@router.get("/mis-horarios", response_model=list[HorarioOut])
def listar(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_medico),
):
    return horario_service.listar_mis_horarios(db, usuario)


@router.put("/{horario_id}", response_model=HorarioOut)
def actualizar(
    horario_id: int,
    data: HorarioUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_medico),
):
    return horario_service.actualizar_horario(db, usuario, horario_id, data)


@router.delete("/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    horario_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_medico),
):
    horario_service.eliminar_horario(db, usuario, horario_id)