"""Servicio SIG Fase 1: proxy IGAC con lista blanca + validación de bbox.

Principios: precarga recortada por predio/lote en oficina (ONLINE/MIXTO),
uso offline en campo desde Dexie (capasIgac). Nunca precarga nacional.
Todo en español, coordenadas cliente en WGS84 (EPSG:4326).
"""
from urllib.parse import urlencode

from ..configuracion import configuracion

# Capas permitidas: nombre lógico -> servicio remoto, capa y descripción.
# Cada capa usa su propio servicio: nunca reutilizar la cartografía básica
# de un municipio para presentarla como agrología o catastro.
CAPAS_PERMITIDAS = {
    "agrologia": {
        "titulo": "Agrología IGAC 1:100.000",
        "capa_remota": "0",  # ArcGIS WMS usa el id numérico de la capa
        "url_wms": "https://mapas.igac.gov.co/server/services/agrologia/suelosdecolombiaaniveldeorden/MapServer/WMSServer",
        "url_rest": "https://mapas.igac.gov.co/server/rest/services/agrologia/suelosdecolombiaaniveldeorden/MapServer/0/query",
        "insignia": "MIXTO",
        "fuente": "IGAC · Suelos y Tierras de Colombia 2016 (1:100.000)",
        "descripcion": "Órdenes de suelos y correlación agrológica nacional.",
    },
    "predial": {
        "titulo": "Catastro rural IGAC",
        "capa_remota": "1",  # R_TERRENO en Dato_Fundamental_Catastro
        "url_wms": "https://mapas.igac.gov.co/server/services/Dato_Fundamental_Catastro/MapServer/WMSServer",
        "url_rest": "https://mapas.igac.gov.co/server/rest/services/Dato_Fundamental_Catastro/MapServer/1/query",
        "insignia": "MIXTO",
        "fuente": "IGAC · Dato Fundamental Catastro (R_TERRENO)",
        "descripcion": "Terrenos rurales catastrales; cobertura parcial según municipio.",
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
        "version": "1.1.1",
        "request": "GetMap",
        "layers": info["capa_remota"],
        "styles": "",
        "srs": "EPSG:4326",
        # WMS 1.1.1 usa siempre orden lon,lat.
        "bbox": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "width": str(ancho),
        "height": str(alto),
        "format": "image/png",
        "transparent": "true",
    }
    return f"{info['url_wms']}?{urlencode(params)}"


def url_rest_getfeature(capa: str, bbox: tuple[float, float, float, float]) -> str:
    """Construye una consulta ArcGIS REST acotada al bbox (GeoJSON).

    IGAC publica estos servicios como MapServer de ArcGIS; sus WFS no
    aceptan GeoJSON. La consulta REST sí devuelve ``f=geojson`` y respeta
    el SRID del cliente (WGS84).
    """
    info = CAPAS_PERMITIDAS[capa]
    params = {
        "where": "1=1",
        "geometry": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": "4326",
        "outSR": "4326",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
    }
    return f"{info['url_rest']}?{urlencode(params)}"


def url_wfs_getfeature(capa: str, bbox: tuple[float, float, float, float]) -> str:
    """Alias de compatibilidad: la precarga usa la consulta REST de ArcGIS."""
    return url_rest_getfeature(capa, bbox)


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
