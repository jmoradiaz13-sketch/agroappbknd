"""Servicio DEM Fase 2: pendiente real con Copernicus GLO-30.

Estrategia offline-first: en oficina (ONLINE) se muestrean elevaciones de las
teselas COG públicas de Copernicus sobre el bbox del lote; el resultado
numérico (pendiente %) se guarda en el lote y viaja a campo offline. No se
descarga el ráster completo: rasterio lee solo la ventana necesaria vía HTTP.
Todo en español.
"""
import math

import rasterio
from rasterio.errors import RasterioError

from ..configuracion import configuracion

DEMO_PENDIENTE_PCT = 12.4
DEMO_DESNIVEL_M = 200.0
FUENTE_DEM = "Copernicus DEM GLO-30 (AWS Open Data) + ficha VSA de campo"
RESOLUCION_DEM_M = 30


class DemNoDisponible(RuntimeError):
    """La tesela DEM no se pudo abrir o no tiene elevación válida."""


def malla_bbox(bbox: tuple[float, float, float, float]) -> list[tuple[float, float]]:
    """Malla 3x3 (lat, lon) sobre el bbox para estimar gradiente."""
    lon_min, lat_min, lon_max, lat_max = bbox
    lons = [lon_min, (lon_min + lon_max) / 2.0, lon_max]
    lats = [lat_min, (lat_min + lat_max) / 2.0, lat_max]
    return [(lat, lon) for lat in lats for lon in lons]


def distancia_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine en metros."""
    r = 6371000.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def pendiente_desde_elevaciones(puntos: list[tuple[float, float]], elevaciones: list[float]) -> dict:
    """Pendiente media y máxima (%) desde malla 3x3: desnivel/distancia*100."""
    centro = puntos[4]
    centro_h = elevaciones[4]
    gradientes = []
    for i, (lat, lon) in enumerate(puntos):
        if i == 4:
            continue
        dist = distancia_m(centro[0], centro[1], lat, lon)
        if dist < 1:
            continue
        gradientes.append(abs(elevaciones[i] - centro_h) / dist * 100.0)
    if not gradientes:
        raise ValueError("malla de elevaciones vacía")
    desnivel = max(elevaciones) - min(elevaciones)
    return {
        "pendiente_pct": round(sum(gradientes) / len(gradientes), 1),
        "pendiente_max_pct": round(max(gradientes), 1),
        "desnivel_m": round(desnivel, 1),
        "n_muestras": len(puntos),
    }


def clasificar(pendiente_pct: float) -> tuple[str, str]:
    if pendiente_pct < 7:
        return ("plano", "Mecanizable. Profundiza ficha física (VESS + densidad).")
    if pendiente_pct <= 25:
        return ("ondulado", "Curvas a nivel y cobertura viva. Revisa erosión en caracterización.")
    return ("empinado", "Cobertura permanente, sin laboreo. Prioriza restauración.")


def _cuadrante(valor: float, positivo: str, negativo: str, ancho: int) -> str:
    entero = math.floor(valor)
    hemisferio = positivo if entero >= 0 else negativo
    return f"{hemisferio}{abs(entero):0{ancho}d}_00"


def nombre_tesela(lat: float, lon: float) -> str:
    """Nombre de tesela Copernicus GLO-30 de 1°x1° que contiene el punto."""
    lat_nombre = _cuadrante(lat, "N", "S", 2)
    lon_nombre = _cuadrante(lon, "E", "W", 3)
    return f"Copernicus_DSM_COG_10_{lat_nombre}_{lon_nombre}_DEM"


def url_tesela(lat: float, lon: float) -> str:
    nombre = nombre_tesela(lat, lon)
    return f"{configuracion.copernicus_dem_url_base.rstrip('/')}/{nombre}/{nombre}.tif"


def _elevaciones_copernicus(puntos: list[tuple[float, float]]) -> list[float]:
    por_tesela: dict[str, list[tuple[int, float, float]]] = {}
    for indice, (lat, lon) in enumerate(puntos):
        por_tesela.setdefault(url_tesela(lat, lon), []).append((indice, lat, lon))

    elevaciones: list[float | None] = [None] * len(puntos)
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        GDAL_HTTP_TIMEOUT=str(max(10, configuracion.sig_tiempo_fuera_seg)),
        GDAL_HTTP_MAX_RETRY="2",
        GDAL_HTTP_RETRY_DELAY="1",
    ):
        for url, muestras in por_tesela.items():
            try:
                with rasterio.open(url) as dataset:
                    nodata = dataset.nodata
                    for indice, lat, lon in muestras:
                        valor = float(next(dataset.sample([(lon, lat)]))[0])
                        if (nodata is not None and valor == nodata) or not math.isfinite(valor):
                            raise DemNoDisponible(f"DEM sin elevación válida en {lat}, {lon}")
                        elevaciones[indice] = valor
            except RasterioError as exc:
                raise DemNoDisponible(f"No se pudo leer la tesela Copernicus GLO-30: {url}") from exc

    if any(valor is None for valor in elevaciones):
        raise DemNoDisponible("DEM devolvió muestras incompletas")
    return [float(valor) for valor in elevaciones]


def muestrear_dem(bbox: tuple[float, float, float, float]) -> dict:
    """Muestrea Copernicus GLO-30 y estima pendiente. Lanza DemNoDisponible si falla."""
    puntos = malla_bbox(bbox)
    elevaciones = _elevaciones_copernicus(puntos)
    estimacion = pendiente_desde_elevaciones(puntos, elevaciones)
    return {
        **estimacion,
        "resolucion_m": RESOLUCION_DEM_M,
        "teselas": sorted({nombre_tesela(lat, lon) for lat, lon in puntos}),
        "fuente": FUENTE_DEM,
    }
