from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RolEnum(str, enum.Enum):
    paciente = "paciente"
    medico = "medico"
    admin = "admin"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolEnum), default=RolEnum.paciente, nullable=False)

    medico = relationship("Medico", back_populates="usuario", uselist=False)
    citas = relationship("Cita", back_populates="paciente")