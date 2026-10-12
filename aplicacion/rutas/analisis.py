"""Análisis espacial MIXTO/ONLINE: DEM→pendiente/RUSLE, IGAC, NDVI (MVP manual)."""
from fastapi import APIRouter, HTTPException, Query

import requests

from ..servicios import sig_cal, sig_dem, sig_igac, sig_ndvi, sig_rusle
from ..servicios import lluvia_ideam as servicio_lluvia

enrutador = APIRouter(prefix="/analisis", tags=["analisis"])


@enrutador.get("/pendiente-rusle")
def pendiente_rusle(
    predio_identificador: str,
    pendiente_pct: float | None = Query(None, ge=0, le=200),
    bbox: str | None = Query(None),
):
    """Clasifica pendiente por lote y orienta manejo. Fase 2 calculará con DEM."""
    if bbox:
        try:
            sig_igac.validar_bbox(bbox)
        except ValueError as e:
            raise HTTPException(400, str(e))
    if pendiente_pct is None:
        return {
            "predio": predio_identificador,
            "estado": "requiere pendiente_pct o precarga DEM (MIXTO)",
            "clases": [
                {"rango": "< 7 %", "manejo": "Plano · mecanizable"},
                {"rango": "7–25 %", "manejo": "Ondulado · curvas a nivel y cobertura"},
                {"rango": "> 25 %", "manejo": "Empinado · cobertura permanente, no laboreo"},
            ],
            "nota": "Registra pendiente_pct del lote o precarga DEM Copernicus GLO-30 en /sig/precarga. RUSLE completo en Fase 2.",
        }
    if pendiente_pct < 7:
        clase, manejo = "plano", "Mecanizable. Profundiza ficha física (VESS + densidad)."
    elif pendiente_pct <= 25:
        clase, manejo = "ondulado", "Curvas a nivel y cobertura viva. Revisa erosión en caracterización."
    else:
        clase, manejo = "empinado", "Cobertura permanente, sin laboreo. Prioriza restauración."
    return {
        "predio": predio_identificador,
        "pendiente_pct": pendiente_pct,
        "clase": clase,
        "manejo": manejo,
        "insignia": "MIXTO",
        "fuente": "Copernicus GLO-30 + ficha VSA de campo",
    }


@enrutador.get("/salud")
def salud():
    return {"estado": "ok", "srid_almacenamiento": 4686, "srid_cliente": 4326}


@enrutador.get("/pendiente-dem")
def pendiente_dem(
    predio_identificador: str,
    bbox: str = Query(...),
    modo: str = Query("real", pattern="^(real|demo)$"),
):
    """Pendiente DEM real por muestreo SRTM (oficina ONLINE). modo=demo sin red."""
    try:
        caja = sig_igac.validar_bbox(bbox)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if modo == "demo":
        clase, manejo = sig_dem.clasificar(sig_dem.DEMO_PENDIENTE_PCT)
        return {
            "predio": predio_identificador,
            "bbox_wgs84": list(caja),
            "pendiente_pct": sig_dem.DEMO_PENDIENTE_PCT,
            "pendiente_max_pct": sig_dem.DEMO_PENDIENTE_PCT,
            "desnivel_m": sig_dem.DEMO_DESNIVEL_M,
            "clase": clase,
            "manejo": manejo,
            "n_muestras": 9,
            "insignia": "MIXTO",
            "fuente": "DEM demo offline (sin red)",
        }
    try:
        estimacion = sig_dem.muestrear_dem(caja)
    except requests.RequestException as e:
        raise HTTPException(502, f"DEM no disponible ahora, usa modo=demo o reintenta en oficina: {e}")
    except ValueError as e:
        raise HTTPException(502, str(e))
    clase, manejo = sig_dem.clasificar(estimacion["pendiente_pct"])
    return {
        "predio": predio_identificador,
        "bbox_wgs84": list(caja),
        **estimacion,
        "clase": clase,
        "manejo": manejo,
        "insignia": "MIXTO",
        "fuente": "SRTM 90m vía OpenTopodata + ficha VSA de campo",
    }


@enrutador.get("/ndvi-serie")
def ndvi_serie(
    predio_identificador: str,
    bbox: str = Query(...),
    modo: str = Query("demo", pattern="^(real|demo)$"),
):
    """Serie temporal NDVI por lote. Sin credenciales Copernicus, usa modo=demo."""
    try:
        caja = sig_igac.validar_bbox(bbox)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if modo == "demo":
        serie = sig_ndvi.serie_demo()
        return {
            "predio": predio_identificador,
            "bbox_wgs84": list(caja),
            "puntos": serie,
            "interpretacion": sig_ndvi.interpretar_serie(serie),
            "insignia": "ONLINE",
            "fuente": "Sentinel-2 demo offline (sin red). Real: Copernicus L2A en oficina.",
        }
    raise HTTPException(
        502,
        "Serie satelital real requiere credenciales Copernicus en oficina. Usa modo=demo o precarga la última serie.",
    )


@enrutador.get("/rusle")
def rusle(
    predio_identificador: str,
    pendiente_pct: float = Query(..., ge=0, le=200),
    cobertura_pct: float = Query(60.0, ge=0, le=100),
    longitud_m: float = Query(50.0, gt=0, le=1000),
    r: float = Query(3000.0, gt=0, description="Erosividad lluvia MJ·mm/ha·h·año (Andina ~3000)"),
    k: float = Query(0.03, gt=0, description="Erodabilidad t·ha·h/ha·MJ·mm (franco ~0.03)"),
    practica: str = Query("sin_practicas", pattern="^(sin_practicas|curvas_nivel|terrazas|cobertura_permanente|bosque_restaurado)$"),
):
    """Pérdida de suelo RUSLE A=R·K·LS·C·P con la pendiente DEM del lote."""
    try:
        resultado = sig_rusle.estimar(r, k, pendiente_pct, longitud_m, cobertura_pct, practica)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        "predio": predio_identificador,
        "pendiente_pct": pendiente_pct,
        **resultado,
        "insignia": "MIXTO",
        "fuente": "Copernicus GLO-30 + ficha VSA de campo",
    }


@enrutador.get("/enmienda-cal")
def enmienda_cal(
    predio_identificador: str,
    aluminio_cmol_kg: float = Query(..., ge=0),
    cice_cmol_kg: float = Query(..., gt=0),
    textura: str = Query("franco", pattern="^(arenoso|franco|arcilloso|limoso)$"),
    al_tolerado_pct: float = Query(20.0, ge=0, le=100),
):
    """Dosis de cal dolomita (t/ha) según Al intercambiable, CICE y textura."""
    try:
        resultado = sig_cal.dosis_cal(aluminio_cmol_kg, cice_cmol_kg, textura, al_tolerado_pct)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        "predio": predio_identificador,
        "aluminio_cmol_kg": aluminio_cmol_kg,
        "cice_cmol_kg": cice_cmol_kg,
        "textura": textura,
        **resultado,
        "insignia": "MIXTO",
        "fuente": sig_cal.FUENTE,
    }


@enrutador.get("/lluvia-ideam")
def lluvia_ideam(
    municipio: str,
    lat: float | None = Query(None),
    lng: float | None = Query(None),
    modo: str = Query("real", pattern="^(real|demo)$"),
):
    """Lluvia anual + IMF de la estación IDEAM más cercana (datos, sin coeficientes R)."""
    if not municipio.strip():
        raise HTTPException(400, "El municipio es obligatorio")
    if modo == "demo":
        demo = dict(servicio_lluvia.DEMO)
        return {
            **demo,
            "imf": servicio_lluvia.indice_fournier(demo["mensuales_mm"]),
            "insignia": "MIXTO",
            "fuente": f"{servicio_lluvia.FUENTE} (demo offline)",
            "nota": "El factor R sigue editable: ningún coeficiente R-lluvia se inventa aquí.",
        }
    try:
        estacion = servicio_lluvia.buscar_estacion(municipio, lat, lng)
    except requests.RequestException as e:
        raise HTTPException(502, f"IDEAM no disponible ahora, usa modo=demo o reintenta en oficina: {e}")
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        **estacion,
        "imf": servicio_lluvia.indice_fournier(estacion["mensuales_mm"]),
        "insignia": "MIXTO",
        "fuente": servicio_lluvia.FUENTE,
        "nota": "El factor R sigue editable: ningún coeficiente R-lluvia se inventa aquí.",
    }
