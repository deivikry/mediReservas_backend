from pydantic import BaseModel
from datetime import datetime


class HorarioCreate(BaseModel):
    fecha_hora: datetime


class HorarioUpdate(BaseModel):
    fecha_hora: datetime


class HorarioOut(BaseModel):
    id: int
    medico_id: int
    fecha_hora: datetime

    class Config:
        from_attributes = True