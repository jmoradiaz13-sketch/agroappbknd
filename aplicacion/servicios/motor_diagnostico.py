"""Motor de diagnóstico: ficha -> lista de hallazgos con porqué + referencia.

No inventa datos: todo umbral viene de aplicacion/datos/referencias.py
que a su vez cita src/*.pdf. El técnico decide (acepta/rechaza/edita).
"""
from ..datos.referencias import POR_PARAMETRO


def diagnosticar(valores: dict) -> list[dict]:
    """valores: dict parametro -> float|None. Retorna hallazgos solo con dato presente."""
    hallazgos: list[dict] = []
    for parametro, rango in POR_PARAMETRO.items():
        valor = valores.get(parametro)
        if valor is None:
            continue
        if valor < rango.deficiente_max:
            estado = "deficiente"
            recomendacion = rango.recomendacion_deficiente
        elif valor > rango.optimo_max:
            estado = "exceso"
            recomendacion = rango.recomendacion_exceso
        else:
            estado = "optimo"
            recomendacion = f"Mantener manejo actual para {parametro}."
        hallazgos.append({
            "parametro": parametro,
            "unidad": rango.unidad,
            "valor": valor,
            "estado": estado,
            "porque": (
                f"Valor {valor} {rango.unidad} "
                f"{'bajo el umbral' if estado == 'deficiente' else 'sobre el umbral' if estado == 'exceso' else 'dentro del rango'} "
                f"[{rango.optimo_min}-{rango.optimo_max} {rango.unidad}]. {recomendacion}"
            ),
            "referencia_bibliografica": rango.fuente,
        })
    return hallazgos


def relaciones_cationicas(valores: dict) -> dict:
    """Cocientes Ca/Mg, Mg/K, (Ca+Mg)/K y Ca/Al solo como valores informativos.

    Sin clasificación de estado: los umbrales dependen del cultivo y se
    interpretan con el manual del laboratorio (cero alucinación, §2.5).
    """
    def cociente(a, b):
        if a is None or b is None or b == 0:
            return None
        return round(a / b, 2)

    ca = valores.get("calcio_cmol_kg")
    mg = valores.get("magnesio_cmol_kg")
    k = valores.get("potasio_cmol_kg")
    al = valores.get("aluminio_cmol_kg")
    return {
        "ca_mg": cociente(ca, mg),
        "mg_k": cociente(mg, k),
        "ca_mg_k": cociente((ca + mg) if ca is not None and mg is not None else None, k),
        "ca_al": cociente(ca, al),
        "nota": "Cocientes informativos en cmol/kg. Interpreta con tu manual según cultivo.",
    }


FUENTE_SALUD = "guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.12-18"

PUNTAJE_POR_ESTADO = {"optimo": 90.0, "deficiente": 40.0, "exceso": 50.0}


def puntaje_salud(hallazgos: list[dict]) -> dict:
    """Soil Health Score 0-100: promedio honesto de hallazgos normalizados.

    No mezcla unidades (% vs mg/kg): cada parámetro aporta 0-100 según su
    estado (óptimo 90, exceso 50, deficiente 40) y se promedia. Trazable a
    FUENTE_SALUD. El técnico decide el manejo final.
    """
    if not hallazgos:
        return {
            "puntaje": 0,
            "nivel": "sin-datos",
            "detalle": "Sin parámetros con dato: registra la ficha de laboratorio.",
            "n_optimo": 0,
            "n_total": 0,
            "fuente": FUENTE_SALUD,
        }
    puntos = [PUNTAJE_POR_ESTADO.get(h.get("estado"), 0.0) for h in hallazgos]
    promedio = round(sum(puntos) / len(puntos))
    n_optimo = sum(1 for h in hallazgos if h.get("estado") == "optimo")
    if promedio >= 80:
        nivel, detalle = "bueno", "Suelo sano y estructurado: mantén cobertura y rotación."
    elif promedio >= 60:
        nivel, detalle = "moderado", "Condición moderada: corrige los parámetros en rojo/amarillo."
    else:
        nivel, detalle = "pobre", "Condición pobre: prioriza MO, cal y cobertura antes de sembrar."
    return {
        "puntaje": promedio,
        "nivel": nivel,
        "detalle": detalle,
        "n_optimo": n_optimo,
        "n_total": len(hallazgos),
        "fuente": FUENTE_SALUD,
    }
