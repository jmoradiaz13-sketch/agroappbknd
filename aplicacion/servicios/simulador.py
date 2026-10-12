"""Motor del simulador: reglas de compatibilidad + escenarios A/B/C + proyección.

Reglas + proyección simple (AGENTS.md §2.5): cada descarte cita su fuente
del banco `datos_bibliograficos/`. Sin invención: lo no medido entra como
supuesto explícito y editable.
"""
from . import sig_rusle

FUENTE_SAF = "saf_cacao_orinoquia (Agrosavia 2025)"
FUENTE_AGROECOLOGIA = "manual_de_agroecologia_y_agroforesteria"
FUENTE_SUELOS = "guia_de_buenas_practicas_para_la_gestion_y_uso_sostenible_de_los_suelos"

# Rotaciones precargadas (AgroLife/CropSyst): secuencia anual + aporte.
ROTACIONES = [
    {
        "id": "maiz-frijol",
        "nombre": "Maíz + fríjol en asocio",
        "secuencia": ["Año 1: maíz + fríjol en surcos alternos", "Año 2: fríjol + abono verde", "Año 3+: rota a cacao joven o descansa con cobertura"],
        "aporte": "N del fríjol + cobertura rápida del maíz",
        "fuente": FUENTE_AGROECOLOGIA,
    },
    {
        "id": "cacao-plátano-guamo",
        "nombre": "Cacao bajo sombrío",
        "secuencia": ["Año 1: plátano + cacao recién sembrado", "Año 2-3: guamo entra como sombrío permanente", "Año 4+: cacao productivo + raleo de plátano"],
        "aporte": "Sombrío gradual 30-50 % e ingreso temprano",
        "fuente": FUENTE_SAF,
    },
    {
        "id": "yuca-cobertura",
        "nombre": "Yuca + cobertura viva",
        "secuencia": ["Año 1: yuca en curvas a nivel", "Año 2: cobertura viva entre calles", "Año 3: descansa con abono verde"],
        "aporte": "Tolera acidez y protege ladera",
        "fuente": FUENTE_AGROECOLOGIA,
    },
    {
        "id": "restauracion-vetiver",
        "nombre": "Restauración con barreras",
        "secuencia": ["Año 1: vetiver en curvas + cobertura", "Año 2-3: guamo y cedro en parches", "Año 4-5: bosque en formación, solo monitoreo"],
        "aporte": "Frena escorrentía y reconstruye suelo",
        "fuente": FUENTE_SUELOS,
    },
]


def rotaciones() -> list[dict]:
    return ROTACIONES

R_DEFECHO = 3000.0
K_DEFECHO = 0.03
LONGITUD_DEFECHO = 50.0


def compatibilidad(especie: dict, sitio: dict) -> dict:
    """Puntaje 0-100 especie×sitio con motivos citados. Descarte duro documentado."""
    motivos = []
    puntaje = 0

    ph = sitio.get("ph")
    if ph is not None and especie.get("ph_min") is not None and especie.get("ph_max") is not None:
        if especie["ph_min"] <= ph <= especie["ph_max"]:
            puntaje += 30
            motivos.append({"regla": "pH en rango", "cumple": True, "cita": FUENTE_SUELOS})
        elif abs(ph - especie["ph_min"] if ph < especie["ph_min"] else ph - especie["ph_max"]) > 1.0:
            return {
                "puntaje": 0,
                "apta": False,
                "motivos": [{"regla": "pH fuera de tolerancia (>1.0)", "cumple": False, "cita": FUENTE_SUELOS}],
            }
        else:
            puntaje += 10
            motivos.append({"regla": "pH marginal (requiere enmienda cal)", "cumple": True, "cita": FUENTE_SUELOS})
    else:
        motivos.append({"regla": "pH supuesto editable (sin dato de ficha)", "cumple": True, "cita": "supuesto"})

    mo = sitio.get("mo_pct")
    if mo is not None and especie.get("mo_min_pct") is not None:
        if mo >= especie["mo_min_pct"]:
            puntaje += 20
            motivos.append({"regla": "MO suficiente", "cumple": True, "cita": FUENTE_SUELOS})
        else:
            motivos.append({"regla": "MO baja: aporta hojarasca/abono verde", "cumple": True, "cita": FUENTE_AGROECOLOGIA})
            puntaje += 5
    else:
        motivos.append({"regla": "MO supuesta editable", "cumple": True, "cita": "supuesto"})

    textura = (sitio.get("textura") or "").lower()
    texturas = [t.lower() for t in (especie.get("texturas") or [])]
    if textura and texturas:
        if textura in texturas:
            puntaje += 20
            motivos.append({"regla": "textura compatible", "cumple": True, "cita": FUENTE_SUELOS})
        else:
            motivos.append({"regla": "textura distinta: vigilar drenaje", "cumple": True, "cita": FUENTE_SUELOS})
    else:
        motivos.append({"regla": "textura supuesta editable", "cumple": True, "cita": "supuesto"})

    pendiente = sitio.get("pendiente_pct")
    max_pend = especie.get("pendiente_max_pct")
    if pendiente is not None and max_pend is not None:
        if pendiente <= max_pend:
            puntaje += 20
            motivos.append({"regla": "pendiente admite la especie", "cumple": True, "cita": FUENTE_SAF})
        else:
            return {
                "puntaje": 0,
                "apta": False,
                "motivos": [{"regla": f"pendiente {pendiente} % supera el máximo {max_pend} %: solo restauración", "cumple": False, "cita": FUENTE_SAF}],
            }
    else:
        motivos.append({"regla": "pendiente supuesta editable", "cumple": True, "cita": "supuesto"})

    zona = (sitio.get("zona_vida") or "").lower()
    zona_esp = (especie.get("zona_vida") or "todas").lower()
    if zona_esp in ("todas", "") or (zona and zona in zona_esp):
        puntaje += 10
        motivos.append({"regla": "zona de vida compatible", "cumple": True, "cita": FUENTE_AGROECOLOGIA})
    else:
        motivos.append({"regla": "zona distinta: valida con técnico local", "cumple": True, "cita": "supuesto"})

    return {"puntaje": min(100, puntaje), "apta": puntaje >= 50, "motivos": motivos}


def proyeccion_cobertura(cobertura_inicial: float, anos: int = 5, k: float = 0.5) -> list[dict]:
    """Curva logística simple 0-5 años hacia 100 % de dosel (AquaCrop simplificado)."""
    import math

    if not 0 < cobertura_inicial < 100:
        raise ValueError("cobertura_inicial debe estar entre 0 y 100 (exclusivo)")
    serie = []
    for ano in range(anos + 1):
        cob = 100.0 / (1.0 + ((100.0 - cobertura_inicial) / cobertura_inicial) * math.exp(-k * ano))
        serie.append({"ano": ano, "cobertura_pct": round(cob, 1)})
    return serie


def _rusle_escenario(pendiente_pct: float, cobertura_pct: float, practica: str) -> dict:
    return sig_rusle.estimar(R_DEFECHO, K_DEFECHO, pendiente_pct, LONGITUD_DEFECHO, cobertura_pct, practica)


def generar_escenarios(sitio: dict, especies: list[dict]) -> list[dict]:
    """Tres escenarios comparables desde el diagnóstico del sitio."""
    pendiente = sitio.get("pendiente_pct")
    if pendiente is None:
        raise ValueError("El sitio requiere pendiente_pct (DEM o registro del lote)")
    cobertura_base = sitio.get("cobertura_pct", 40.0)
    aptas = [e for e in especies if compatibilidad(e, sitio)["apta"]]
    nombres = [e.get("nombre_comun", "?") for e in aptas]

    productivas = [n for n, e in zip(nombres, aptas) if "ingreso" in (e.get("rol") or "").lower() or "sombr" in (e.get("rol") or "").lower()]
    fijadoras = [n for n, e in zip(nombres, aptas) if "nitr" in (e.get("rol") or "").lower() or "abono" in (e.get("rol") or "").lower()]
    protectoras = [n for n, e in zip(nombres, aptas) if "cobertura" in (e.get("rol") or "").lower() or "biol" in (e.get("rol") or "").lower()]

    antes = _rusle_escenario(pendiente, cobertura_base, "sin_practicas")
    planes = [
        {
            "tipo": "A",
            "nombre": "A · Productivo",
            "usos": {"Cultivos": 55, "SAF / agroforestería": 30, "Conservación / parches": 10, "Corredores / cercas vivas": 5},
            "componentes": (productivas[:2] or nombres[:2]),
            "practica": "curvas_nivel",
            "cobertura_meta": 60.0,
            "rotacion": "Año 1 maíz + fríjol; año 2 cacao joven con plátano; año 3+ dosel productivo.",
        },
        {
            "tipo": "B",
            "nombre": "B · Restauración",
            "usos": {"Conservación / parches": 55, "Corredores / cercas vivas": 20, "SAF / agroforestería": 15, "Cultivos": 10},
            "componentes": (protectoras[:2] or nombres[:2]),
            "practica": "bosque_restaurado",
            "cobertura_meta": 90.0,
            "rotacion": "Año 1 vetiver + cobertura; año 2-3 guamo/cedro; año 5+ bosque en formación.",
        },
        {
            "tipo": "C",
            "nombre": "C · Integrado (recomendado)",
            "usos": {"Cultivos": 40, "SAF / agroforestería": 30, "Conservación / parches": 20, "Corredores / cercas vivas": 10},
            "componentes": ((fijadoras[:1] + productivas[:1]) or nombres[:2]),
            "practica": "cobertura_permanente",
            "cobertura_meta": 75.0,
            "rotacion": "Año 1 maíz-fríjol en franjas; año 2 SAF cacao-guamo; conservación permanente en ladera.",
        },
    ]
    escenarios = []
    for p in planes:
        despues = _rusle_escenario(pendiente, p["cobertura_meta"], p["practica"])
        escenarios.append({
            **p,
            "especies_aptas": len(aptas),
            "rusle_antes_t_ha_ano": antes["perdida_t_ha_ano"],
            "rusle_despues_t_ha_ano": despues["perdida_t_ha_ano"],
            "proyeccion_cobertura": proyeccion_cobertura(cobertura_base),
            "conservacion_pct": p["usos"]["Conservación / parches"] + p["usos"]["Corredores / cercas vivas"],
            "fuente": f"{FUENTE_SAF}; {FUENTE_AGROECOLOGIA}; {FUENTE_SUELOS}",
        })
    return escenarios
