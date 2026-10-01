from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.cita import Cita, EstadoCita
from app.models.usuario import Usuario
from app.schemas.cita import CitaCreate


def crear_cita(db: Session, usuario: Usuario, data: CitaCreate) -> Cita:
    cita = Cita(
        paciente_id=usuario.id,        # ← del TOKEN, no del body
        medico_id=data.medico_id,
        horario_id=data.horario_id,
        fecha_hora=data.fecha_hora,
        estado=EstadoCita.pendiente,
    )
    db.add(cita)
    db.commit()
    db.refresh(cita)
    return cita


def listar_mis_citas(db: Session, usuario: Usuario) -> list[Cita]:
    return db.query(Cita).filter(Cita.paciente_id == usuario.id).all()


def cancelar_cita(db: Session, usuario: Usuario, cita_id: int) -> Cita:
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada",
        )
    if cita.paciente_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cancelar citas de otro paciente",
        )
    cita.estado = EstadoCita.cancelada
    db.commit()
    db.refresh(cita)
    return cita