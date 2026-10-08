"""Monitoreo: seguimiento del lote con indicadores, observaciones, fotos."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, JSON, DateTime, func
from geoalchemy2 import Geometry
from ..base_datos import Base


class Monitoreo(Base):
    __tablename__ = "monitoreos"

    id = Column(Integer, primary_key=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    indicadores = Column(JSON, nullable=True, default=dict)
    observaciones = Column(Text, nullable=True)
    fotografias = Column(JSON, nullable=True, default=list)  # URLs/rutas locales
    coordenadas = Column(Geometry("POINT", srid=4686), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
