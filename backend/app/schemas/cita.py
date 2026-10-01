from pydantic import BaseModel
from datetime import datetime
from app.models.cita import EstadoCita


class CitaCreate(BaseModel):
    medico_id: int
    horario_id: int
    fecha_hora: datetime


class CitaOut(BaseModel):
    id: int
    paciente_id: int
    medico_id: int
    horario_id: int
    fecha_hora: datetime
    estado: EstadoCita

    class Config:
        from_attributes = True