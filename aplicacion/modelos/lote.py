"""Lote: subdivisión del predio con manejo independiente (prompt Opus + AGENTS)."""
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON, DateTime, func
from geoalchemy2 import Geometry
from ..base_datos import Base


class Lote(Base):
    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True)
    predio_id = Column(Integer, ForeignKey("predios.id"), nullable=False)
    nombre = Column(String(200), nullable=False)
    area_ha = Column(Float, nullable=True)
    geometria = Column(Geometry("POLYGON", srid=4686), nullable=False)
    uso_actual = Column(String(200), nullable=True)
    usos_historicos = Column(JSON, nullable=True, default=list)
    pendiente_pct = Column(Float, nullable=True)
    cobertura = Column(String(200), nullable=True)
    # Caracterización biofísica MVP: clima, zona_vida, erosion
    clima = Column(String(100), nullable=True)
    zona_vida = Column(String(100), nullable=True)
    erosion = Column(String(100), nullable=True)
    notas = Column(Text, nullable=True)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now())
