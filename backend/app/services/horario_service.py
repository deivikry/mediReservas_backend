from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.horario import Horario
from app.models.medico import Medico
from app.models.usuario import Usuario
from app.schemas.horario import HorarioCreate, HorarioUpdate


def _get_medico_del_usuario(db: Session, usuario: Usuario) -> Medico:
    medico = db.query(Medico).filter(Medico.usuario_id == usuario.id).first()
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene perfil de médico",
        )
    return medico


def crear_horario(db: Session, usuario: Usuario, data: HorarioCreate) -> Horario:
    medico = _get_medico_del_usuario(db, usuario)
    horario = Horario(medico_id=medico.id, fecha_hora=data.fecha_hora)
    db.add(horario)
    db.commit()
    db.refresh(horario)
    return horario


def listar_mis_horarios(db: Session, usuario: Usuario) -> list[Horario]:
    medico = _get_medico_del_usuario(db, usuario)
    return db.query(Horario).filter(Horario.medico_id == medico.id).all()


def _obtener_horario_propio(db: Session, usuario: Usuario, horario_id: int) -> Horario:
    medico = _get_medico_del_usuario(db, usuario)
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if not horario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horario no encontrado",
        )
    if horario.medico_id != medico.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes modificar horarios de otro médico",
        )
    return horario


def actualizar_horario(db: Session, usuario: Usuario, horario_id: int, data: HorarioUpdate) -> Horario:
    horario = _obtener_horario_propio(db, usuario, horario_id)
    horario.fecha_hora = data.fecha_hora
    db.commit()
    db.refresh(horario)
    return horario


def eliminar_horario(db: Session, usuario: Usuario, horario_id: int) -> None:
    horario = _obtener_horario_propio(db, usuario, horario_id)
    db.delete(horario)
    db.commit()