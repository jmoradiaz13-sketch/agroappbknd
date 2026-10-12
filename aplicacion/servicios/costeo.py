"""Costeo de escenarios 5 años (COP): supuestos explícitos y editables.

Agrak/Farmbrite enseñan que el productor decide por costo, no solo por
toneladas. Este modelo es deliberadamente simple y honesto: jornal,
jornales de establecimiento, insumos y mantenimiento anual por tipo de
escenario. Todo supuesto se devuelve para edición en la UI.
"""
from __future__ import annotations

JORNAL_DEFECHO = 60000.0
ANOS = 5

# Por tipo de escenario: jornales/ha de establecimiento, insumos/ha,
# mantenimiento anual/ha. Valores orientativos Colombia 2025-2026.
PARAMETROS = {
    "A": {"jornales": 40.0, "insumos_ha": 1200000.0, "mantenimiento_ha_ano": 800000.0},
    "B": {"jornales": 25.0, "insumos_ha": 400000.0, "mantenimiento_ha_ano": 150000.0},
    "C": {"jornales": 35.0, "insumos_ha": 800000.0, "mantenimiento_ha_ano": 500000.0},
}


def costear(tipo: str, area_ha: float, jornal: float = JORNAL_DEFECHO) -> dict:
    if tipo not in PARAMETROS:
        raise ValueError(f"tipo no válido. Usa: {sorted(PARAMETROS)}")
    if area_ha <= 0:
        raise ValueError("area_ha debe ser positiva")
    if jornal <= 0:
        raise ValueError("El jornal debe ser positivo")
    p = PARAMETROS[tipo]
    establecimiento = area_ha * (p["jornales"] * jornal + p["insumos_ha"])
    mantenimiento = area_ha * p["mantenimiento_ha_ano"] * ANOS
    total = round(establecimiento + mantenimiento, 0)
    return {
        "tipo": tipo,
        "area_ha": area_ha,
        "anos": ANOS,
        "establecimiento_cop": round(establecimiento, 0),
        "mantenimiento_cop": round(mantenimiento, 0),
        "total_cop": total,
        "costo_ha_cop": round(total / area_ha, 0),
        "supuestos": [
            f"Jornal ${jornal:,.0f}/día",
            f"Establecimiento {p['jornales']} jornales/ha + insumos ${p['insumos_ha']:,.0f}/ha",
            f"Mantenimiento ${p['mantenimiento_ha_ano']:,.0f}/ha/año por {ANOS} años",
        ],
    }
