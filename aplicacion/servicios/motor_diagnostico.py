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
