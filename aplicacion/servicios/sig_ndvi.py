"""Servicio NDVI Fase 2: serie temporal Sentinel-2 L2A real vía Copernicus.

En oficina (ONLINE) se consulta Sentinel Hub Statistical API con credenciales
OAuth2 de Copernicus Data Space. El resultado numérico se cachea en el
dispositivo y viaja a campo para consulta offline. Sin credenciales el modo
real responde con error explícito; ``modo=demo`` queda solo para pruebas.
Todo en español.
"""
import calendar
from datetime import date, datetime, timedelta, timezone

import requests

from ..configuracion import configuracion

SERIE_DEMO = [
    {"fecha": "2026-07-15", "ndvi": 0.68, "nubosidad_pct": 5, "nota": "referencia seca"},
    {"fecha": "2026-08-12", "ndvi": 0.52, "nubosidad_pct": 35, "nota": "nubosidad parcial"},
    {"fecha": "2026-09-10", "ndvi": 0.28, "nubosidad_pct": 10, "nota": "posible estrés"},
]

FUENTE_REAL = "Sentinel-2 L2A · Copernicus Data Space (NDVI 10 m)"
EVALSCRIPT = """//VERSION=3
function setup() {
  return {
    input: [{ bands: ["B04", "B08", "SCL", "dataMask"] }],
    output: { bands: ["ndvi", "nubosidad"], sampleType: "FLOAT32" }
  };
}
function evaluatePixel(sample) {
  const ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04 + 0.00001);
  const nube = [3, 8, 9, 10, 11].includes(sample.SCL) ? 1 : 0;
  return [ndvi, nube];
}
"""


class CredencialesFaltantes(RuntimeError):
    """No hay credenciales Copernicus configuradas para el modo real."""


def clasificar_ndvi(ndvi: float) -> tuple[str, str]:
    if ndvi < 0.3:
        return ("suelo/estrés", "Suelo desnudo o estrés: visita la zona y registra VSA + foto cenital.")
    if ndvi <= 0.6:
        return ("transición", "Transición: verifica cobertura y compara con la ficha de suelos.")
    return ("vigoroso", "Vigoroso: mantiene cobertura; programa siguiente lectura.")


def interpretar_serie(puntos: list[dict]) -> dict:
    """Tendencia entre primera y última lectura + alerta de zona débil."""
    if len(puntos) < 2:
        return {"tendencia": "estable", "delta": 0.0, "alerta": None}
    delta = round(puntos[-1]["ndvi"] - puntos[0]["ndvi"], 2)
    tendencia = "a la baja" if delta < -0.1 else ("al alza" if delta > 0.1 else "estable")
    alerta = None
    debiles = [p for p in puntos if p["ndvi"] < 0.3]
    if debiles:
        alerta = f"Zona débil el {debiles[-1]['fecha']} (NDVI {debiles[-1]['ndvi']}): crea punto de muestreo."
    return {"tendencia": tendencia, "delta": delta, "alerta": alerta}


def serie_demo() -> list[dict]:
    serie = []
    for p in SERIE_DEMO:
        clase, manejo = clasificar_ndvi(p["ndvi"])
        serie.append({**p, "clase": clase, "manejo": manejo})
    return serie


def _restar_meses(fecha: date, meses: int) -> date:
    total = fecha.year * 12 + (fecha.month - 1) - meses
    anio, mes = divmod(total, 12)
    mes += 1
    dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)


def rango_serie(meses: int | None = None, hoy: date | None = None) -> tuple[str, str]:
    hasta = hoy or date.today()
    desde = _restar_meses(hasta, meses or configuracion.copernicus_meses_ndvi)
    return desde.isoformat(), hasta.isoformat()


def _token_copernicus() -> str:
    if not configuracion.copernicus_id_cliente or not configuracion.copernicus_secreto_cliente:
        raise CredencialesFaltantes(
            "Faltan COPERNICUS_ID_CLIENTE y COPERNICUS_SECRETO_CLIENTE en el servidor."
        )
    respuesta = requests.post(
        configuracion.copernicus_token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": configuracion.copernicus_id_cliente,
            "client_secret": configuracion.copernicus_secreto_cliente,
        },
        timeout=max(20, configuracion.sig_tiempo_fuera_seg * 2),
    )
    respuesta.raise_for_status()
    cuerpo = respuesta.json()
    token = cuerpo.get("access_token")
    if not token:
        raise ValueError("Copernicus no devolvió access_token")
    return str(token)


def cuerpo_estadisticas(caja: tuple[float, float, float, float], desde: str, hasta: str) -> dict:
    return {
        "input": {
            "bounds": {
                "bbox": list(caja),
                "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {"maxCloudCoverage": 80, "mosaickingOrder": "leastCC"},
                }
            ],
        },
        "aggregation": {
            "timeRange": {"from": f"{desde}T00:00:00Z", "to": f"{hasta}T23:59:59Z"},
            "aggregationInterval": {"of": "P30D"},
            "evalscript": EVALSCRIPT,
            "resx": 10,
            "resy": 10,
        },
        "calculations": {"default": {}},
    }


def _stats(item: dict, indice: int) -> dict | None:
    salidas = item.get("outputs") or []
    if not salidas:
        return None
    bandas = salidas[0].get("bands") or []
    if indice >= len(bandas):
        return None
    stats = bandas[indice].get("stats") or {}
    if int(stats.get("sampleCount") or 0) <= 0:
        return None
    return stats


def parsear_estadisticas(cuerpo: dict) -> list[dict]:
    puntos: list[dict] = []
    for item in cuerpo.get("data") or []:
        stats_ndvi = _stats(item, 0)
        if not stats_ndvi:
            continue
        media = stats_ndvi.get("mean")
        if media is None:
            continue
        ndvi = round(float(media), 2)
        if not -1 <= ndvi <= 1:
            continue
        stats_nube = _stats(item, 1)
        nubosidad = 0
        if stats_nube and stats_nube.get("mean") is not None:
            nubosidad = round(float(stats_nube["mean"]) * 100)
        intervalo = item.get("interval") or {}
        fecha = str(intervalo.get("from") or "")[:10]
        if not fecha:
            continue
        clase, manejo = clasificar_ndvi(ndvi)
        nota = f"Sentinel-2 L2A · nubosidad {nubosidad}%"
        puntos.append(
            {
                "fecha": fecha,
                "ndvi": ndvi,
                "nubosidad_pct": nubosidad,
                "nota": nota,
                "clase": clase,
                "manejo": manejo,
            }
        )
    puntos.sort(key=lambda p: p["fecha"])
    return puntos


def serie_real(caja: tuple[float, float, float, float]) -> dict:
    """Consulta Sentinel-2 L2A y devuelve la serie agregada cada 30 días."""
    token = _token_copernicus()
    desde, hasta = rango_serie()
    respuesta = requests.post(
        configuracion.copernicus_estadisticas_url,
        json=cuerpo_estadisticas(caja, desde, hasta),
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=max(30, configuracion.sig_tiempo_fuera_seg * 4),
    )
    respuesta.raise_for_status()
    puntos = parsear_estadisticas(respuesta.json())
    if not puntos:
        raise ValueError(
            "Sentinel-2 no devolvió lecturas válidas para este lote y periodo; intenta otro bbox o fecha."
        )
    return {
        "puntos": puntos,
        "desde": desde,
        "hasta": hasta,
        "fuente": FUENTE_REAL,
    }
