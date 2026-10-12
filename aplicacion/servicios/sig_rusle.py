"""Servicio RUSLE Fase 3: pérdida de suelo A = R·K·LS·C·P (t/ha/año).

MVP honesto: LS se deriva de la pendiente DEM; K, R, C y P los aporta el
técnico (con valores andinos por defecto) o la ficha de campo. Sin DEM se
usa la pendiente registrada del lote. Todo en español.
"""
import math

# K orientativo (t·ha·h/ha·MJ·mm) por textura al tacto.
K_POR_TEXTURA = {
    "arenoso": 0.02,
    "franco": 0.03,
    "arcilloso": 0.025,
    "limoso": 0.045,
}

# P por práctica de conservación (AGENTS.md §4.2: 0.1 a 1.0).
P_POR_PRACTICA = {
    "sin_practicas": 1.0,
    "curvas_nivel": 0.6,
    "terrazas": 0.4,
    "cobertura_permanente": 0.3,
    "bosque_restaurado": 0.1,
}


def factor_ls(pendiente_pct: float, longitud_m: float = 50.0) -> dict:
    """LS Wischmeier-Smith/Foster: L=(λ/22.13)^m, S según pendiente."""
    if pendiente_pct < 0 or longitud_m <= 0:
        raise ValueError("pendiente y longitud deben ser positivas")
    if pendiente_pct >= 5:
        m = 0.5
    elif pendiente_pct >= 3:
        m = 0.4
    else:
        m = 0.3
    ele = (longitud_m / 22.13) ** m
    theta = math.atan(pendiente_pct / 100.0)
    if pendiente_pct < 9:
        ese = 10.8 * math.sin(theta) + 0.03
    else:
        ese = 16.8 * math.sin(theta) - 0.5
    return {"ls": round(ele * ese, 2), "l": round(ele, 2), "s": round(ese, 2), "m": m}


def factor_c(cobertura_pct: float) -> float:
    """C desde cobertura %: C=(1-cob)^1.5, mínimo 0.01 (suelo cubierto)."""
    if not 0 <= cobertura_pct <= 100:
        raise ValueError("cobertura_pct debe estar entre 0 y 100")
    return round(max(0.01, (1.0 - cobertura_pct / 100.0) ** 1.5), 3)


def clasificar_a(perdida: float) -> tuple[str, str]:
    if perdida < 10:
        return ("leve", "Erosión tolerable. Mantén cobertura y monitorea VSA.")
    if perdida <= 50:
        return ("moderada", "Curvas a nivel + cobertura viva. Revisa compactación e infiltración.")
    if perdida <= 150:
        return ("alta", "Terrazas o barreras vivas + cobertura permanente. Prioriza este lote.")
    return ("muy alta", "Riesgo crítico: cobertura permanente inmediata, sin laboreo. Restaura primero aquí.")


# Nivel Plan Maestro (Bajo/Moderado/Severo/Crítico) + semáforo, sin romper `clase`.
# Guardián contra la erosión: < 5 t/ha/año (insignia).
FUENTE_RUSLE = "Copernicus GLO-30 + ficha VSA de campo (A = R·K·LS·C·P)"
UMBRAL_GUARDIAN_T_HA_ANO = 5.0


def nivel_riesgo(perdida: float) -> tuple[str, str]:
    """Bajo <5, Moderado 5-15, Severo 15-50, Crítico >50. Colores en `semaforo`."""
    if perdida < UMBRAL_GUARDIAN_T_HA_ANO:
        return ("bajo", "verde")
    if perdida < 15:
        return ("moderado", "amarillo")
    if perdida <= 50:
        return ("severo", "naranja")
    return ("critico", "rojo")


def estimar(r: float, k: float, pendiente_pct: float, longitud_m: float, cobertura_pct: float, practica: str) -> dict:
    if r <= 0 or k <= 0:
        raise ValueError("R y K deben ser positivos")
    if practica not in P_POR_PRACTICA:
        raise ValueError(f"práctica no válida. Usa: {sorted(P_POR_PRACTICA)}")
    ls = factor_ls(pendiente_pct, longitud_m)
    ce = factor_c(cobertura_pct)
    pe = P_POR_PRACTICA[practica]
    perdida = round(r * k * ls["ls"] * ce * pe, 1)
    clase, manejo = clasificar_a(perdida)
    nivel, semaforo = nivel_riesgo(perdida)
    return {
        "perdida_t_ha_ano": perdida,
        "clase": clase,
        "manejo": manejo,
        "nivel_riesgo": nivel,
        "semaforo": semaforo,
        "guardian_erosion": perdida < UMBRAL_GUARDIAN_T_HA_ANO,
        "fuente": FUENTE_RUSLE,
        "factores": {"r": r, "k": k, **ls, "c": ce, "p": pe},
    }
