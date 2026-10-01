from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class EstadoCita(str, enum.Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    cancelada = "cancelada"


class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("medicos.id"), nullable=False)
    horario_id = Column(Integer, ForeignKey("horarios.id"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    estado = Column(Enum(EstadoCita), default=EstadoCita.pendiente, nullable=False)

    paciente = relationship("Usuario", back_populates="citas")
    medico = relationship("Medico", back_populates="citas")