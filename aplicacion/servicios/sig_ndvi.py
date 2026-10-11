"""Servicio NDVI Fase 3: serie temporal Sentinel-2 (B8-B4)/(B8+B4), 10 m.

Estrategia honesta offline-first: en oficina (ONLINE) se descarga la serie
recortada por lote desde Copernicus; en campo se usa la última serie
precargada. Sin credenciales Copernicus configuradas, el modo real responde
502 y se usa modo=demo (determinista, para tests y campo sin red).
Todo en español.
"""

SERIE_DEMO = [
    {"fecha": "2026-07-15", "ndvi": 0.68, "nubosidad_pct": 5, "nota": "referencia seca"},
    {"fecha": "2026-08-12", "ndvi": 0.52, "nubosidad_pct": 35, "nota": "nubosidad parcial"},
    {"fecha": "2026-09-10", "ndvi": 0.28, "nubosidad_pct": 10, "nota": "posible estrés"},
]


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
