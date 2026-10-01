from pydantic import BaseModel


class MedicoCreate(BaseModel):
    usuario_id: int
    especialidad: str


class MedicoOut(BaseModel):
    id: int
    usuario_id: int
    especialidad: str

    class Config:
        from_attributes = True