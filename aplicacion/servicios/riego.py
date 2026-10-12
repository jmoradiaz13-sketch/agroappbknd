"""Asistente de riego: balance simple FAO-56/AquaCrop con supuestos explícitos.

ETo por Hargreaves (solo Tmax/Tmin + latitud, sin estación completa),
lluvia efectiva al 80 % y Kc por cultivo. Si el técnico trae ETo de
estación, se usa directo. Fuente: FAO-56 + AquaCrop.
"""
import math

FUENTE = "FAO-56 + AquaCrop (FAO)"

KC_POR_CULTIVO = {
    "cacao": 1.05,
    "maiz": 1.0,
    "frijol": 0.9,
    "platano": 1.0,
    "yuca": 0.8,
    "pasto": 0.9,
    "bosque": 1.1,
    "hortalizas": 0.9,
}


def eto_hargreaves(tmax: float, tmin: float, latitud: float, dia_ano: int) -> float:
    """ETo diaria (mm) Hargreaves-Samani. Valida rangos tropicales."""
    if not tmin < tmax:
        raise ValueError("tmax debe ser mayor que tmin")
    if not -90 <= latitud <= 90:
        raise ValueError("latitud fuera de rango")
    if not 1 <= dia_ano <= 366:
        raise ValueError("dia_ano debe estar entre 1 y 366")
    lat = math.radians(latitud)
    dr = 1 + 0.033 * math.cos(2 * math.pi * dia_ano / 365)
    delta = 0.409 * math.sin(2 * math.pi * dia_ano / 365 - 1.39)
    ws = math.acos(max(-1.0, min(1.0, -math.tan(lat) * math.tan(delta))))
    ra = 37.6 * dr * (ws * math.sin(lat) * math.sin(delta) + math.cos(lat) * math.cos(delta) * math.sin(ws))
    tmedia = (tmax + tmin) / 2
    return round(max(0.0, 0.0023 * (tmedia + 17.8) * math.sqrt(tmax - tmin) * ra), 2)


def balance(
    cultivo: str,
    lluvia_mm: float,
    eto_mm: float | None = None,
    tmax: float | None = None,
    tmin: float | None = None,
    latitud: float = 4.6,
    dia_ano: int = 200,
) -> dict:
    if cultivo not in KC_POR_CULTIVO:
        raise ValueError(f"cultivo no válido. Usa: {sorted(KC_POR_CULTIVO)}")
    if lluvia_mm < 0:
        raise ValueError("La lluvia no puede ser negativa")
    if eto_mm is None:
        if tmax is None or tmin is None:
            raise ValueError("Aporta ETo de estación o Tmax/Tmin para Hargreaves")
        eto_mm = eto_hargreaves(tmax, tmin, latitud, dia_ano)
    kc = KC_POR_CULTIVO[cultivo]
    et_cultivo = round(kc * eto_mm, 2)
    lluvia_efectiva = round(lluvia_mm * 0.8, 2)
    lamina = round(max(0.0, et_cultivo - lluvia_efectiva), 2)
    if lamina == 0:
        manejo = f"Sin riego hoy: la lluvia efectiva ({lluvia_efectiva} mm) cubre la ET del cultivo ({et_cultivo} mm)."
    elif lamina < 3:
        manejo = f"Riego ligero de {lamina} mm hoy o acumula 2 días. Revisa mulch y cobertura."
    else:
        manejo = f"Aplica {lamina} mm hoy, temprano en la mañana. Fracciona si supera 8 mm para evitar escorrentía."
    return {
        "cultivo": cultivo,
        "kc": kc,
        "eto_mm": eto_mm,
        "et_cultivo_mm": et_cultivo,
        "lluvia_efectiva_mm": lluvia_efectiva,
        "lamina_riego_mm": lamina,
        "manejo": manejo,
    }
