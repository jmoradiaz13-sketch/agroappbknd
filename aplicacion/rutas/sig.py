"""Rutas SIG Fase 1: IGAC primero, precarga oficina -> campo offline."""
import requests
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..configuracion import configuracion
from ..servicios import sig_igac

enrutador = APIRouter(prefix="/sig", tags=["sig"])


class SolicitudPrecarga(BaseModel):
    predio_identificador: str
    bbox: str  # 'lon_min,lat_min,lon_max,lat_max' en WGS84
    capas: list[str] = ["agrologia", "predial"]


@enrutador.get("/capas")
def listar_capas():
    """Lista blanca de capas SIG con conectividad y fuente oficial."""
    return {
        "capas": [
            {"id": cid, **info} for cid, info in sig_igac.CAPAS_PERMITIDAS.items()
        ],
        "nota": "MIXTO: online en oficina, offline en campo desde precarga. Fuentes: IGAC · Copernicus.",
    }


@enrutador.get("/igac/mapa")
def mapa_igac(capa: str = Query("agrologia"), bbox: str = Query(...)):
    """Devuelve URL WMS GetMap para visor online en oficina (PC)."""
    if capa not in sig_igac.CAPAS_PERMITIDAS:
        raise HTTPException(400, f"capa '{capa}' no permitida. Usa: {sorted(sig_igac.CAPAS_PERMITIDAS)}")
    try:
        caja = sig_igac.validar_bbox(bbox)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        "capa": capa,
        "url_wms": sig_igac.url_wms_getmap(capa, caja),
        "srs": "EPSG:4326",
        "insignia": "MIXTO",
        "fuente": sig_igac.CAPAS_PERMITIDAS[capa]["fuente"],
    }


@enrutador.get("/igac/geojson")
def geojson_igac(
    capa: str = Query("agrologia"),
    bbox: str = Query(...),
    modo: str = Query("real", pattern="^(real|demo)$"),
):
    """Proxy WFS: descarga vector recortado para precarga. modo=demo sin red (tests/campo)."""
    if capa not in sig_igac.CAPAS_PERMITIDAS:
        raise HTTPException(400, f"capa '{capa}' no permitida. Usa: {sorted(sig_igac.CAPAS_PERMITIDAS)}")
    try:
        caja = sig_igac.validar_bbox(bbox)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if modo == "demo":
        return {
            "capa": capa,
            "bbox_wgs84": list(caja),
            "geojson": sig_igac.POLIGONO_DEMO,
            "fuente": "IGAC demo offline (sin red)",
            "insignia": "MIXTO",
        }
    url = sig_igac.url_wfs_getfeature(capa, caja)
    try:
        respuesta = requests.get(url, timeout=configuracion.sig_tiempo_fuera_seg)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except requests.RequestException as e:
        raise HTTPException(502, f"IGAC no disponible ahora, usa modo=demo o reintenta en oficina: {e}")
    except ValueError:
        raise HTTPException(502, "IGAC devolvió respuesta no válida (no GeoJSON)")
    return {
        "capa": capa,
        "bbox_wgs84": list(caja),
        "geojson": datos,
        "fuente": sig_igac.CAPAS_PERMITIDAS[capa]["fuente"],
        "insignia": "MIXTO",
    }


@enrutador.post("/precarga")
def crear_precarga(solicitud: SolicitudPrecarga):
    """Plan de precarga oficina->campo con verificación del límite 200 MB."""
    for capa in solicitud.capas:
        if capa not in ("agrologia", "predial", "pendiente", "ndvi"):
            raise HTTPException(400, f"capa '{capa}' no válida para precarga")
    if not solicitud.predio_identificador.strip():
        raise HTTPException(400, "predio_identificador es obligatorio")
    try:
        caja = sig_igac.validar_bbox(solicitud.bbox)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return sig_igac.plan_precarga(solicitud.predio_identificador.strip(), caja, solicitud.capas)
