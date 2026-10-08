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
