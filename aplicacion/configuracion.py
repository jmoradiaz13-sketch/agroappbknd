"""Configuración en español (pydantic-settings)."""
from pydantic_settings import BaseSettings


class Configuracion(BaseSettings):
    url_base_datos: str = "postgresql+psycopg2://agroapp:agroapp123@localhost:5432/agroapp_bd"
    srid_almacenamiento: int = 4686  # MAGNA-SIRGAS
    srid_cliente: int = 4326  # WGS84 Leaflet
    url_frontal: str = "http://localhost:5173"  # CORS: URL pública del frontend
    mongodb_uri: str | None = None  # Atlas (futuro: sincronización/documentos)
    # SIG Fase 1 (IGAC primero, offline al máximo): proxy con lista blanca.
    igac_wms_base: str = "https://mapas2.igac.gov.co/server/services/carto/carto1000lavega25402000/MapServer/WMSServer"
    igac_wfs_base: str = "https://mapas2.igac.gov.co/server/services/carto/carto1000lavega25402000/MapServer/WFSServer"
    sig_tiempo_fuera_seg: int = 20  # timeout proxy IGAC
    sig_area_max_km2: float = 50.0  # precarga recortada por predio/lote, nunca nacional

    class Config:
        env_file = ".env"
        extra = "ignore"  # .env trae claves de docker-compose ajenas a la app


configuracion = Configuracion()
