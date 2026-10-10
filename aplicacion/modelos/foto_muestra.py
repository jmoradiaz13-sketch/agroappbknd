"""Fotos de muestra offline: serie versionada, jamás se actualiza ni borra.

La imagen vive en BYTEA (fotos de campo comprimidas en cliente, ~200-400 KB).
Miniatura aparte para listados rápidos.
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, LargeBinary, Text, DateTime, func
from .predio import Predio  # noqa: F401  (asegura registro de tablas)
from .ficha_suelo import FichaSuelo  # noqa: F401
from ..base_datos import Base


class FotoMuestra(Base):
    __tablename__ = "fotos_muestra"

    id = Column(Integer, primary_key=True)
    ficha_id = Column(Integer, ForeignKey("fichas_suelo.id"), nullable=True)
    predio_identificador = Column(String(100), nullable=False)
    lote_nombre = Column(String(200), nullable=True)
    tipo = Column(String(20), nullable=False, default="muestra")  # muestra|vess|cobertura|punto
    imagen = Column(LargeBinary, nullable=False)
    miniatura = Column(LargeBinary, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    cobertura_pct = Column(Float, nullable=True)
    fecha = Column(Date, nullable=False)
    observaciones = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
