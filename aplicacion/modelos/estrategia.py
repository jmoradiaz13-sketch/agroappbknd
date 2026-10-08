"""Estrategia agroecológica INMUTABLE: serie temporal ligada a una ficha.

Igual que FichaSuelo: nunca UPDATE/DELETE, solo INSERT nueva versión.
El técnico decide: decision_tecnico en aceptada|rechazada|editada.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, JSON, DateTime, func
from ..base_datos import Base


class Estrategia(Base):
    __tablename__ = "estrategias"

    id = Column(Integer, primary_key=True)
    ficha_id = Column(Integer, ForeignKey("fichas_suelo.id"), nullable=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    version = Column(Integer, nullable=False)
    tipo = Column(String(50), nullable=True)  # agroforesteria|rotacion|cobertura|restauracion
    especies = Column(JSON, nullable=True, default=list)
    practicas = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="propuesta")  # propuesta|aprobada|implementada|en_monitoreo
    fecha_propuesta = Column(Date, nullable=True)
    descripcion = Column(Text, nullable=False)
    decision_tecnico = Column(String(20), nullable=False, default="aceptada")
    referencia_bibliografica = Column(String(300), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
