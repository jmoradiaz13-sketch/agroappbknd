"""Lluvia IDEAM para el factor R del RUSLE (datos, no coeficientes).

Fuente: Normales Climatológicas IDEAM en datos.gov.co (recurso nsz2-kzcq,
par_metro PRECIPITACIÓN). Devuelve lluvia anual, mensuales e IMF
(Σ p_i²/P, matemática pura). El factor R sigue editable por el técnico:
ningún coeficiente R-lluvia se inventa aquí (§2.5).
"""
import math

import requests

from ..configuracion import configuracion

URL_SOCRATA = "https://www.datos.gov.co/resource/nsz2-kzcq.json"
FUENTE = "IDEAM · Normales Climatológicas (datos.gov.co nsz2-kzcq)"

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

DEMO = {
    "estacion": "Tibaitatá (demo offline)",
    "municipio": "Mosquera",
    "departamento": "Cundinamarca",
    "periodo": "1981-2010",
    "mensuales_mm": [70.0, 85.0, 110.0, 120.0, 95.0, 55.0, 40.0, 45.0, 70.0, 110.0, 105.0, 80.0],
    "anual_mm": 985.0,
}


def indice_fournier(mensuales: list[float]) -> float:
    anual = sum(mensuales)
    if anual <= 0:
        raise ValueError("Lluvia anual inválida para el índice de Fournier")
    return round(sum(p * p for p in mensuales) / anual, 1)


def _distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return math.hypot(lat1 - lat2, lon1 - lon2)


def buscar_estacion(municipio: str, lat: float | None = None, lng: float | None = None) -> dict:
    """Estación PRECIPITACIÓN del municipio; la más cercana a (lat,lng) si se dan."""
    params = {
        "$where": f"upper(municipio)='{municipio.strip().upper()}' AND par_metro='PRECIPITACIÓN'",
        "$limit": "50",
    }
    respuesta = requests.get(URL_SOCRATA, params=params, timeout=configuracion.sig_tiempo_fuera_seg)
    respuesta.raise_for_status()
    filas = respuesta.json()
    if not filas:
        raise ValueError(f"Sin estaciones PRECIPITACIÓN para '{municipio}' en IDEAM. Verifica el nombre.")
    candidatas = []
    for f in filas:
        try:
            mensuales = [float((f.get(m) or "0").replace(",", ".")) for m in MESES]
            anual = float((f.get("anual") or "0").replace(",", "."))
        except (ValueError, TypeError):
            continue
        if anual <= 0:
            continue
        dist = None
        if lat is not None and lng is not None:
            try:
                dist = _distancia(lat, lng, float(f.get("latitud") or 0), float(f.get("longitud") or 0))
            except (ValueError, TypeError):
                dist = None
        candidatas.append((dist if dist is not None else 999.0, {
            "estacion": f.get("estaci_n") or f.get("nombreestacion") or "sin nombre",
            "municipio": f.get("municipio"),
            "departamento": f.get("departamento"),
            "periodo": f.get("periodo"),
            "mensuales_mm": mensuales,
            "anual_mm": anual,
        }))
    if not candidatas:
        raise ValueError(f"Estaciones sin datos útiles para '{municipio}'.")
    candidatas.sort(key=lambda c: c[0])
    return candidatas[0][1]
