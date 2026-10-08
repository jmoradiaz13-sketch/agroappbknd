"""ReferenciaBibliografica: entidad de primera clase (prompt Opus).

Cada recomendación debe vincularse a una o más referencias.
Origen: datos_bibliograficos/references.json generado del script de extracción.
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, func
from ..base_datos import Base


class ReferenciaBibliografica(Base):
    __tablename__ = "referencias_bibliograficas"

    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)  # articulo|libro|manual|norma
    autores = Column(String(500), nullable=True)
    anio = Column(String(20), nullable=True)
    titulo = Column(String(500), nullable=False)
    fuente = Column(String(500), nullable=False)  # src/*.pdf o DOI/URL
    doi = Column(String(200), nullable=True)
    datos_extraidos = Column(JSON, nullable=True, default=dict)
    uso_en_proyecto = Column(String(200), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
