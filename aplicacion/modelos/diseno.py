"""Diseño agroecológico INMUTABLE: serie temporal por unidad de producción.

Simulador de diseño agroecológico: parte de terrenos caracterizados o desde
cero con datos mínimos. La referencia bibliográfica es OPCIONAL en el
simulador (se cuadra después). Versionado igual que fichas: nunca UPDATE.
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from .predio import Predio  # noqa: F401  (asegura registro de tablas)
from ..base_datos import Base


class Diseno(Base):
    __tablename__ = "disenos"

    id = Column(Integer, primary_key=True)
    predio_id = Column(Integer, ForeignKey("predios.id"), nullable=True)  # nulo si se simula desde cero
    unidad_nombre = Column(String(200), nullable=False)
    fecha = Column(Date, nullable=False)
    version = Column(Integer, nullable=False)  # 1,2,3... por unidad
    area_total_ha = Column(Float, nullable=True)
    zona_clima = Column(String(200), nullable=True)
    objetivo = Column(Text, nullable=True)
    tipo_diseno = Column(String(50), nullable=True)  # SAF|silvopastoril|policultivo|corredor|mixto
    nivel_transicion = Column(Integer, nullable=True)  # 1-4 Gliessman
    usos_suelo = Column(JSONB, nullable=False, default=list)  # [{uso, porcentaje}]
    componentes = Column(JSONB, nullable=False, default=list)  # [{rol, especie, detalle}]
    rotacion_asociacion = Column(Text, nullable=True)
    referencia_bibliografica = Column(String(300), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
