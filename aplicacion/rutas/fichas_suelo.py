"""Rutas de fichas: solo crea nuevas versiones, jamás actualiza ni borra."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio
from ..modelos.ficha_suelo import FichaSuelo
from ..esquemas.ficha import FichaSueloCrear

enrutador = APIRouter(prefix="/fichas-suelo", tags=["fichas-suelo"])


@enrutador.post("/nueva-version")
def crear_nueva_version(datos: FichaSueloCrear, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=datos.predio_identificador).first()
    if not predio:
        raise HTTPException(404, f"Predio {datos.predio_identificador} no encontrado")
    max_version = sesion.query(func.max(FichaSuelo.version)).filter_by(predio_id=predio.id).scalar() or 0
    ficha = FichaSuelo(
        predio_id=predio.id,
        fecha=datos.fecha,
        version=max_version + 1,
        profundidad_cm=datos.profundidad_cm,
        laboratorio_observador=datos.laboratorio_observador,
        ph_agua=datos.ph_agua,
        ph_kcl=datos.ph_kcl,
        calcio_cmol_kg=datos.calcio_cmol_kg,
        magnesio_cmol_kg=datos.magnesio_cmol_kg,
        potasio_cmol_kg=datos.potasio_cmol_kg,
        sodio_cmol_kg=datos.sodio_cmol_kg,
        cic_cmol_kg=datos.cic_cmol_kg,
        fosforo_mg_kg=datos.fosforo_mg_kg,
        materia_organica_pct=datos.materia_organica_pct,
        nitrogeno_pct=datos.nitrogeno_pct,
        conductividad_ds_m=datos.conductividad_ds_m,
        hierro_mg_kg=datos.hierro_mg_kg,
        manganeso_mg_kg=datos.manganeso_mg_kg,
        zinc_mg_kg=datos.zinc_mg_kg,
        cobre_mg_kg=datos.cobre_mg_kg,
        boro_mg_kg=datos.boro_mg_kg,
        arena_pct=datos.arena_pct,
        limo_pct=datos.limo_pct,
        arcilla_pct=datos.arcilla_pct,
        referencia_bibliografica=datos.referencia_bibliografica,
    )
    sesion.add(ficha)
    sesion.commit()
    sesion.refresh(ficha)
    return {"id": ficha.id, "version": ficha.version, "porque": f"Sugerencia trazada a {ficha.referencia_bibliografica}"}
