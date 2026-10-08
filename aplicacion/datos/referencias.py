"""Catálogo de rangos agronómicos con trazabilidad a src/*.pdf.

REGLA AGENTS.md §3.1 NO INVENTAR DATOS: cada rango tiene `fuente` obligatoria.
Estos son rangos iniciales de trabajo extraídos de las guías FAO/USDA presentes
en src/ — el técnico debe validarlos en campo académico antes de producción.

Fuentes principales:
- guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf
- guia_para_la_evaluacion_visual_de_la_calidad_del_suelo.pdf
- guia_de_buenas_practicas_para_la_gestion_y_uso_sostenible_de_los_suelos.pdf
- descripcion_y_muestreo_de_suelos.pdf
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RangoParametro:
    parametro: str
    unidad: str
    deficiente_max: float  # por debajo => deficiente
    optimo_min: float
    optimo_max: float  # por encima => exceso
    fuente: str
    recomendacion_deficiente: str
    recomendacion_exceso: str


CATALOGO_RANGOS: list[RangoParametro] = [
    RangoParametro(
        parametro="materia_organica_pct", unidad="%",
        deficiente_max=2.0, optimo_min=2.0, optimo_max=5.0,
        fuente="guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.12-18",
        recomendacion_deficiente="Incorporar abonos orgánicos / cobertura; verificar con análisis visual (guia_para_la_evaluacion_visual_de_la_calidad_del_suelo.pdf).",
        recomendacion_exceso="Mantener cobertura; evitar exceso de N orgánico que desbalancee C/N.",
    ),
    RangoParametro(
        parametro="fosforo_mg_kg", unidad="mg/kg",
        deficiente_max=15.0, optimo_min=15.0, optimo_max=40.0,
        fuente="guia_de_buenas_practicas_para_la_gestion_y_uso_sostenible_de_los_suelos.pdf cap. fertilidad",
        recomendacion_deficiente="Evaluar enmienda fosfórica de liberación lenta + micorrizas (enfoque agroecológico); confirmar con muestreo según descripcion_y_muestreo_de_suelos.pdf.",
        recomendacion_exceso="Suspender aporte de P; riesgo de fijación y escorrentía.",
    ),
    RangoParametro(
        parametro="potasio_cmol_kg", unidad="cmol/kg",
        deficiente_max=0.2, optimo_min=0.2, optimo_max=0.6,
        fuente="guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.20-25",
        recomendacion_deficiente="Aporte potásico fraccionado + cenizas reguladas; revisar lixiviación.",
        recomendacion_exceso="Revisar antagonismo K-Ca-Mg; suspender aporte.",
    ),
    RangoParametro(
        parametro="calcio_cmol_kg", unidad="cmol/kg",
        deficiente_max=3.0, optimo_min=3.0, optimo_max=10.0,
        fuente="guia_de_buenas_practicas_para_la_gestion_y_uso_sostenible_de_los_suelos.pdf cap. acidez",
        recomendacion_deficiente="Evaluar encalado según pH y saturación de Al; validar con técnico.",
        recomendacion_exceso="Vigilar pH alcalino y disponibilidad de micronutrientes.",
    ),
    RangoParametro(
        parametro="magnesio_cmol_kg", unidad="cmol/kg",
        deficiente_max=0.8, optimo_min=0.8, optimo_max=3.0,
        fuente="guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.20-25",
        recomendacion_deficiente="Corregir relación Ca/Mg; considerar dolomita si Ca también bajo.",
        recomendacion_exceso="Revisar balance catiónico.",
    ),
    RangoParametro(
        parametro="conductividad_ds_m", unidad="dS/m",
        deficiente_max=0.0, optimo_min=0.0, optimo_max=2.0,
        fuente="guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf cap. salinidad",
        recomendacion_deficiente="Sin acción (no hay deficiencia por sales bajas).",
        recomendacion_exceso="Riesgo salinidad: mejorar drenaje, lavar sales, evitar fertilizantes salinos.",
    ),
    RangoParametro(
        parametro="nitrogeno_pct", unidad="%",
        deficiente_max=0.1, optimo_min=0.1, optimo_max=0.3,
        fuente="manual_de_agroecologia_y_agroforesteria._practicas_para_una_agricultura_ecologica.pdf cap. fertilidad",
        recomendacion_deficiente="Leguminosas de cobertura / abono verde; fraccionar N orgánico.",
        recomendacion_exceso="Reducir aporte nitrogenado; riesgo lixiviación.",
    ),
]

POR_PARAMETRO = {r.parametro: r for r in CATALOGO_RANGOS}
