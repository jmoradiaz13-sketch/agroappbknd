"""Configuración en español (pydantic-settings)."""
from pydantic_settings import BaseSettings


class Configuracion(BaseSettings):
    url_base_datos: str = "postgresql+psycopg2://agroapp:agroapp123@localhost:5432/agroapp_bd"
    srid_almacenamiento: int = 4686  # MAGNA-SIRGAS
    srid_cliente: int = 4326  # WGS84 Leaflet
    url_frontal: str = "http://localhost:5173"  # CORS: URL pública del frontend
    mongodb_uri: str | None = None  # Atlas (futuro: sincronización/documentos)

    class Config:
        env_file = ".env"
        extra = "ignore"  # .env trae claves de docker-compose ajenas a la app


configuracion = Configuracion()
