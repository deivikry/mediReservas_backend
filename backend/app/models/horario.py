from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Horario(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    medico_id = Column(Integer, ForeignKey("medicos.id"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)

    medico = relationship("Medico", back_populates="horarios")