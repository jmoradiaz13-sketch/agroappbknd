"""Rutas de diagnóstico: calcula al vuelo + historial inmutable."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio
from ..modelos.ficha_suelo import FichaSuelo
from ..modelos.estrategia import Estrategia
from ..esquemas.diagnostico import DiagnosticoRespuesta, EstrategiaCrear
from ..servicios.motor_diagnostico import diagnosticar, puntaje_salud, relaciones_cationicas

enrutador = APIRouter(prefix="/diagnostico", tags=["diagnostico"])


def _ficha_a_valores(ficha: FichaSuelo) -> dict:
    return {
        "materia_organica_pct": ficha.materia_organica_pct,
        "fosforo_mg_kg": ficha.fosforo_mg_kg,
        "potasio_cmol_kg": ficha.potasio_cmol_kg,
        "calcio_cmol_kg": ficha.calcio_cmol_kg,
        "magnesio_cmol_kg": ficha.magnesio_cmol_kg,
        "conductividad_ds_m": ficha.conductividad_ds_m,
        "nitrogeno_pct": ficha.nitrogeno_pct,
    }


def _valores_relaciones(ficha: FichaSuelo) -> dict:
    return {
        "calcio_cmol_kg": ficha.calcio_cmol_kg,
        "magnesio_cmol_kg": ficha.magnesio_cmol_kg,
        "potasio_cmol_kg": ficha.potasio_cmol_kg,
        "aluminio_cmol_kg": getattr(ficha, "aluminio_cmol_kg", None),
    }


@enrutador.get("/{identificador}/ultimo", response_model=DiagnosticoRespuesta)
def ultimo_diagnostico(identificador: str, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=identificador).first()
    if not predio:
        raise HTTPException(404, "Predio no encontrado")
    ficha = (
        sesion.query(FichaSuelo).filter_by(predio_id=predio.id)
        .order_by(FichaSuelo.version.desc()).first()
    )
    if not ficha:
        raise HTTPException(404, "Sin fichas para este predio")
    valores = _ficha_a_valores(ficha)
    hallazgos = diagnosticar(valores)
    return {
        "predio_identificador": identificador,
        "ficha_version": ficha.version,
        "hallazgos": hallazgos,
        "puntaje_salud": puntaje_salud(hallazgos),
        "relaciones": relaciones_cationicas(_valores_relaciones(ficha)),
    }


@enrutador.get("/{identificador}/historial")
def historial(identificador: str, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=identificador).first()
    if not predio:
        raise HTTPException(404, "Predio no encontrado")
    fichas = (
        sesion.query(FichaSuelo).filter_by(predio_id=predio.id)
        .order_by(FichaSuelo.version.desc()).all()
    )
    return [
        {"version": f.version, "fecha": f.fecha, "referencia": f.referencia_bibliografica}
        for f in fichas
    ]


@enrutador.post("/estrategias/nueva-version")
def crear_estrategia(datos: EstrategiaCrear, sesion: Session = Depends(obtener_sesion)):
    max_v = sesion.query(func.max(Estrategia.version)).filter_by(ficha_id=datos.ficha_id).scalar() or 0
    est = Estrategia(
        ficha_id=datos.ficha_id, version=max_v + 1, descripcion=datos.descripcion,
        decision_tecnico=datos.decision_tecnico,
        referencia_bibliografica=datos.referencia_bibliografica,
    )
    sesion.add(est)
    sesion.commit()
    sesion.refresh(est)
    return {"id": est.id, "version": est.version}
