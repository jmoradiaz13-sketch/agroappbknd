"""Servicio DEM Fase 2: pendiente real por muestreo de elevaciones (SRTM, sin richdem).

Estrategia offline-first: en oficina (ONLINE) se muestrean elevaciones del
DEM global sobre el bbox del lote; el resultado numérico (pendiente %) se
guarda en el lote y viaja a campo offline. No se descarga el ráster completo.
Todo en español.
"""
import math

import requests

from ..configuracion import configuracion

URL_ELEVACION = "https://api.opentopodata.org/v1/srtm90m"

# Demo determinista (tests y campo sin red): desnivel 200 m en ~1,6 km.
DEMO_PENDIENTE_PCT = 12.4
DEMO_DESNIVEL_M = 200.0


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


def muestrear_dem(bbox: tuple[float, float, float, float]) -> dict:
    """Muestrea SRTM vía OpenTopodata y estima pendiente. Lanza en error de red."""
    puntos = malla_bbox(bbox)
    ubicaciones = "|".join(f"{lat},{lon}" for lat, lon in puntos)
    respuesta = requests.get(
        URL_ELEVACION,
        params={"locations": ubicaciones},
        timeout=configuracion.sig_tiempo_fuera_seg,
    )
    respuesta.raise_for_status()
    cuerpo = respuesta.json()
    resultados = cuerpo.get("results", [])
    if len(resultados) != len(puntos):
        raise ValueError("DEM devolvió muestras incompletas")
    elevaciones = []
    for r in resultados:
        h = r.get("elevation")
        if h is None:
            raise ValueError("DEM sin elevación en un punto (nubosidad/sombra del modelo)")
        elevaciones.append(float(h))
    return pendiente_desde_elevaciones(puntos, elevaciones)
