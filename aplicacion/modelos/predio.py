"""Modelo Predio: geometría almacenada en MAGNA-SIRGAS EPSG:4686."""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func
from geoalchemy2 import Geometry
from ..base_datos import Base


class Predio(Base):
    __tablename__ = "predios"

    id = Column(Integer, primary_key=True)
    identificador = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    propietario = Column(String(200), nullable=True)
    documento = Column(String(50), nullable=True)
    contacto = Column(String(200), nullable=True)
    municipio = Column(String(100), nullable=True)
    departamento = Column(String(100), nullable=True)
    area_total_ha = Column(Float, nullable=True)
    notas = Column(Text, nullable=True)
    # Polígono en EPSG:4686. El cliente envía EPSG:4326 y se transforma con ST_Transform.
    geometria = Column(Geometry("POLYGON", srid=4686), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now())
