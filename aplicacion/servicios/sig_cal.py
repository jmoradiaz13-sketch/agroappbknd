"""Servicio de enmiendas §4.3: cal dolomita según Al intercambiable y textura.

Fórmula base AGENTS.md: Dosis = (Al − (Al_tolerado × CICE / 100)) × factor,
factor 1.5 (arenoso) a 2.0 (arcilloso/limoso) por capacidad buffer.
Fuente: guia_de_buenas_practicas_para_la_gestion_y_uso_sostenible_de_los_suelos.
Todo en español, unidades cmol/kg y t/ha.
"""
from __future__ import annotations

FACTOR_POR_TEXTURA = {
    "arenoso": 1.5,
    "franco": 1.75,
    "arcilloso": 2.0,
    "limoso": 2.0,
}

FUENTE = "guia_de_buenas_practicas_para_la_gestion_y_uso_sostenible_de_los_suelos"

# Validación de dosis (patrón cuaderno digital): máximo por aplicación
# para evitar bloqueo de micronutrientes y pérdidas por escorrentía.
DOSIS_MAX_APLICACION = 2.5


def dosis_cal(
    aluminio_cmol_kg: float,
    cice_cmol_kg: float,
    textura: str,
    al_tolerado_pct: float = 20.0,
) -> dict:
    if cice_cmol_kg <= 0:
        raise ValueError("CICE debe ser positiva")
    if aluminio_cmol_kg < 0:
        raise ValueError("El aluminio intercambiable no puede ser negativo")
    if textura not in FACTOR_POR_TEXTURA:
        raise ValueError(f"textura no válida. Usa: {sorted(FACTOR_POR_TEXTURA)}")
    if not 0 <= al_tolerado_pct <= 100:
        raise ValueError("al_tolerado_pct debe estar entre 0 y 100")
    saturacion_actual = round(aluminio_cmol_kg / cice_cmol_kg * 100, 1)
    exceso = aluminio_cmol_kg - (al_tolerado_pct * cice_cmol_kg / 100)
    if exceso <= 0:
        return {
            "dosis_t_ha": 0.0,
            "clase": "no requiere",
            "manejo": f"Saturación de Al {saturacion_actual} % dentro de meta (≤ {al_tolerado_pct} %). Mantén MO y monitorea pH.",
            "saturacion_al_pct": saturacion_actual,
            "factor_textura": FACTOR_POR_TEXTURA[textura],
        }
    dosis = round(exceso * FACTOR_POR_TEXTURA[textura], 2)
    clase = "alta" if dosis > 3 else "moderada"
    import math

    aplicaciones = max(1, math.ceil(dosis / DOSIS_MAX_APLICACION))
    return {
        "dosis_t_ha": dosis,
        "clase": clase,
        "manejo": (
            f"Aplica {dosis} t/ha de cal dolomita en {aplicaciones} aplicación(es) "
            f"de {round(dosis / aplicaciones, 2)} t/ha (máx {DOSIS_MAX_APLICACION} t/ha por vez, cada 60 días) "
            f"e incorpora con materia orgánica. Re-muestrea pH y Al a los 6 meses."
        ),
        "aplicaciones": aplicaciones,
        "dosis_por_aplicacion_t_ha": round(dosis / aplicaciones, 2),
        "saturacion_al_pct": saturacion_actual,
        "factor_textura": FACTOR_POR_TEXTURA[textura],
    }
