"""Punto de muestreo GPS: marca de campo vinculada a predio y lote (Etapa 7)."""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func
from ..base_datos import Base


class PuntoMuestreo(Base):
    __tablename__ = "puntos_muestreo"

    id = Column(Integer, primary_key=True)
    predio_identificador = Column(String(50), nullable=False)
    lote_nombre = Column(String(200), nullable=True)
    codigo = Column(String(50), nullable=False, unique=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    fecha = Column(Date, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
