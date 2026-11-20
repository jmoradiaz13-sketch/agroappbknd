"""Configuración en español (pydantic-settings)."""
from pydantic_settings import BaseSettings


class Configuracion(BaseSettings):
    url_base_datos: str = "postgresql+psycopg2://agroapp:agroapp123@localhost:5432/agroapp_bd"
    srid_almacenamiento: int = 4686  # MAGNA-SIRGAS
    srid_cliente: int = 4326  # WGS84 Leaflet
    url_frontal: str = "http://localhost:5173"  # CORS: URL pública del frontend
    mongodb_uri: str | None = None  # Atlas (futuro: sincronización/documentos)
    # SIG Fase 1 (IGAC primero, offline al máximo): proxy con lista blanca.
    # Las URLs concretas viven en sig_igac.CAPAS_PERMITIDAS porque cada
    # capa (agrología, catastro) pertenece a un servicio distinto.
    sig_tiempo_fuera_seg: int = 20  # timeout proxy IGAC
    sig_area_max_km2: float = 50.0  # precarga recortada por predio/lote, nunca nacional

    # Fase 2: integraciones reales Copernicus.
    # DEM GLO-30 se lee directo del bucket público (sin credenciales).
    copernicus_dem_url_base: str = "https://copernicus-dem-30m.s3.amazonaws.com"
    # NDVI Sentinel-2 L2A vía Sentinel Hub Statistical API (CDSE).
    copernicus_id_cliente: str | None = None
    copernicus_secreto_cliente: str | None = None
    copernicus_token_url: str = (
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    )
    copernicus_estadisticas_url: str = "https://sh.dataspace.copernicus.eu/api/v1/statistics"
    copernicus_meses_ndvi: int = 6

    class Config:
        env_file = ".env"
        extra = "ignore"  # .env trae claves de docker-compose ajenas a la app


configuracion = Configuracion()
