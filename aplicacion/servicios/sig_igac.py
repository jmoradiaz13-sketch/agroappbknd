"""Servicio SIG Fase 1: proxy IGAC con lista blanca + validación de bbox.

Principios: precarga recortada por predio/lote en oficina (ONLINE/MIXTO),
uso offline en campo desde Dexie (capasIgac). Nunca precarga nacional.
Todo en español, coordenadas cliente en WGS84 (EPSG:4326).
"""
from urllib.parse import urlencode

from ..configuracion import configuracion

# Capas permitidas: nombre lógico -> capa remota + tipo + descripción.
CAPAS_PERMITIDAS = {
    "agrologia": {
        "titulo": "Agrología IGAC",
        "capa_remota": "carto1000lavega25402000",
        "insignia": "MIXTO",
        "fuente": "IGAC · Colombia en Mapas (WMS/WFS)",
        "descripcion": "Clases agrológicas y aptitud de suelos por polígono.",
    },
    "predial": {
        "titulo": "Predial y veredas",
        "capa_remota": "carto1000lavega25402000",
        "insignia": "MIXTO",
        "fuente": "IGAC · Geoportal / Catastro",
        "descripcion": "Límites prediales, veredas y municipios de referencia.",
    },
}

# Colombia continental aproximada en WGS84 (lon_min, lat_min, lon_max, lat_max).
BBOX_COLOMBIA = (-79.5, -4.5, -66.5, 13.0)

POLIGONO_DEMO = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"capa": "agrologia", "clase": "IVs", "fuente": "IGAC demo offline"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-74.06, 4.66], [-74.03, 4.66], [-74.03, 4.63], [-74.06, 4.63], [-74.06, 4.66]]],
            },
        }
    ],
}


def validar_bbox(bbox: str) -> tuple[float, float, float, float]:
    """Valida 'lon_min,lat_min,lon_max,lat_max' dentro de Colombia y con área acotada."""
    try:
        partes = [float(x.strip()) for x in bbox.split(",")]
    except ValueError:
        raise ValueError("bbox debe ser 'lon_min,lat_min,lon_max,lat_max' en WGS84")
    if len(partes) != 4:
        raise ValueError("bbox debe tener 4 números: lon_min,lat_min,lon_max,lat_max")
    lon_min, lat_min, lon_max, lat_max = partes
    if not (lon_min < lon_max and lat_min < lat_max):
        raise ValueError("bbox inválido: min debe ser menor que max")
    c_lon_min, c_lat_min, c_lon_max, c_lat_max = BBOX_COLOMBIA
    if not (c_lon_min <= lon_min <= c_lon_max and c_lon_min <= lon_max <= c_lon_max):
        raise ValueError("bbox fuera de Colombia (longitud -79.5 a -66.5)")
    if not (c_lat_min <= lat_min <= c_lat_max and c_lat_min <= lat_max <= c_lat_max):
        raise ValueError("bbox fuera de Colombia (latitud -4.5 a 13.0)")
    # Área aproximada en km2 (1 grado ≈ 111 km, corrección por latitud media).
    lat_media = abs((lat_min + lat_max) / 2.0)
    factor = 111.0 * 111.0 * max(0.5, __import__("math").cos(__import__("math").radians(lat_media)))
    area_km2 = abs(lon_max - lon_min) * abs(lat_max - lat_min) * factor
    if area_km2 > configuracion.sig_area_max_km2:
        raise ValueError(f"bbox de {area_km2:.1f} km² supera el máximo de {configuracion.sig_area_max_km2} km² por precarga")
    return (lon_min, lat_min, lon_max, lat_max)


def url_wms_getmap(capa: str, bbox: tuple[float, float, float, float], ancho: int = 1024, alto: int = 1024) -> str:
    """Construye URL WMS GetMap para visualización online en oficina (PC)."""
    info = CAPAS_PERMITIDAS[capa]
    params = {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetMap",
        "layers": info["capa_remota"],
        "styles": "",
        "crs": "EPSG:4326",
        "bbox": f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}",
        "width": str(ancho),
        "height": str(alto),
        "format": "image/png",
        "transparent": "true",
    }
    return f"{configuracion.igac_wms_base}?{urlencode(params)}"


def url_wfs_getfeature(capa: str, bbox: tuple[float, float, float, float]) -> str:
    """Construye URL WFS GetFeature para descarga vectorial recortada (precarga)."""
    info = CAPAS_PERMITIDAS[capa]
    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": info["capa_remota"],
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "bbox": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
    }
    return f"{configuracion.igac_wfs_base}?{urlencode(params)}"


def plan_precarga(predio_identificador: str, bbox: tuple[float, float, float, float], capas: list[str]) -> dict:
    """Plan de precarga oficina->campo: capas, peso estimado y verificación 200 MB."""
    pesos_mb = {"agrologia": 2.0, "predial": 1.0, "pendiente": 4.0, "ndvi": 8.0}
    detalle = []
    total = 0.0
    for capa in capas:
        peso = pesos_mb.get(capa, 1.0)
        total += peso
        detalle.append({"capa": capa, "peso_estimado_mb": peso})
    cabe = total <= 200.0
    return {
        "predio": predio_identificador,
        "bbox_wgs84": list(bbox),
        "capas": detalle,
        "peso_total_mb": round(total, 2),
        "limite_mb": 200,
        "cabe_en_cache": cabe,
        "pasos": [
            "1. Con wifi en oficina, descarga cada capa recortada por bbox.",
            "2. Guarda GeoJSON en Dexie capasIgac y GeoTIFF en geotiffs.",
            "3. En campo trabaja offline; al volver sincroniza puntos y fotos.",
        ],
        "fuentes": "IGAC · Copernicus GLO-30 · Sentinel-2 L2A",
    }
