"""Configuración en español (pydantic-settings)."""
from pydantic_settings import BaseSettings


class Configuracion(BaseSettings):
    url_base_datos: str = "postgresql+psycopg2://agroapp:agroapp123@localhost:5432/agroapp_bd"
    srid_almacenamiento: int = 4686  # MAGNA-SIRGAS
    srid_cliente: int = 4326  # WGS84 Leaflet

    class Config:
        env_file = ".env"


configuracion = Configuracion()
