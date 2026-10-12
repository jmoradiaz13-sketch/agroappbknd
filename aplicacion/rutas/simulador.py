"""Rutas del simulador: diagnóstico del sitio -> escenarios A/B/C -> plan."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..servicios import simulador
from ..servicios import costeo as servicio_costeo
from ..servicios import riego as servicio_riego

enrutador = APIRouter(prefix="/simulador", tags=["simulador"])


class EspecieEntrada(BaseModel):
    nombre_comun: str
    rol: str | None = None
    ph_min: float | None = None
    ph_max: float | None = None
    mo_min_pct: float | None = None
    texturas: list[str] | None = None
    pendiente_max_pct: float | None = None
    zona_vida: str | None = None


class SitioEntrada(BaseModel):
    ph: float | None = None
    mo_pct: float | None = None
    textura: str | None = None
    pendiente_pct: float | None = None
    zona_vida: str | None = None
    cobertura_pct: float = 40.0


class EscenariosEntrada(BaseModel):
    sitio: SitioEntrada
    especies: list[EspecieEntrada] = []


@enrutador.post("/compatibilidad")
def compatibilidad(especie: EspecieEntrada, sitio: SitioEntrada):
    """Puntaje 0-100 especie×sitio con motivos citados."""
    return {
        "especie": especie.nombre_comun,
        **simulador.compatibilidad(especie.model_dump(), sitio.model_dump()),
        "insignia": "MIXTO",
    }


@enrutador.post("/escenarios")
def escenarios(entrada: EscenariosEntrada):
    """Genera escenarios A productivo, B restauración y C integrado."""
    try:
        lista = simulador.generar_escenarios(
            entrada.sitio.model_dump(), [e.model_dump() for e in entrada.especies]
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"escenarios": lista, "insignia": "MIXTO"}


@enrutador.post("/proyeccion")
def proyeccion(cobertura_inicial: float, anos: int = 5):
    """Curva logística de cobertura 0-5 años (AquaCrop simplificado)."""
    try:
        serie = simulador.proyeccion_cobertura(cobertura_inicial, anos)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"serie": serie, "insignia": "MIXTO"}


@enrutador.post("/costos")
def costos(tipo: str, area_ha: float, jornal: float = servicio_costeo.JORNAL_DEFECHO):
    """Costo 5 años del escenario con supuestos editables (COP)."""
    try:
        resultado = servicio_costeo.costear(tipo, area_ha, jornal)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {**resultado, "insignia": "MIXTO"}


@enrutador.get("/rotaciones")
def rotaciones():
    """Rotaciones y asociaciones precargadas con su aporte y fuente."""
    return {"rotaciones": simulador.rotaciones(), "insignia": "MIXTO"}


@enrutador.post("/riego")
def riego(
    cultivo: str,
    lluvia_mm: float,
    eto_mm: float | None = None,
    tmax: float | None = None,
    tmin: float | None = None,
    latitud: float = 4.6,
    dia_ano: int = 200,
):
    """Lámina de riego del día: ET×Kc menos lluvia efectiva (FAO-56)."""
    try:
        resultado = servicio_riego.balance(cultivo, lluvia_mm, eto_mm, tmax, tmin, latitud, dia_ano)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {**resultado, "insignia": "MIXTO", "fuente": servicio_riego.FUENTE}
