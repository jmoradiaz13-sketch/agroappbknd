"""Propietario/productor del predio (Plan Maestro Etapa 1).

Dato mutable de gestión (no es ficha de suelo): se permite actualizar.
Cédula opcional por privacidad de datos.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from ..base_datos import Base


class Propietario(Base):
    __tablename__ = "propietarios"

    id = Column(Integer, primary_key=True)
    predio_id = Column(Integer, ForeignKey("predios.id"), nullable=False, unique=True)
    nombre_completo = Column(String(200), nullable=False)
    cedula = Column(String(50), nullable=True)
    contacto = Column(String(200), nullable=True)
    tenencia = Column(String(50), nullable=True)  # propiedad|arrendamiento|sucesion|otro
    vocacion = Column(String(100), nullable=True)  # cafe|ganaderia|cacao|policultivo|otro
    mano_obra_familiar = Column(Integer, nullable=True)  # personas disponibles
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now())
