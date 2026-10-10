"""Rutas del simulador: crea versiones de diseño, jamás actualiza ni borra."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio
from ..modelos.diseno import Diseno
from ..esquemas.diseno import DisenoCrear

enrutador = APIRouter(prefix="/disenos", tags=["disenos"])


@enrutador.post("/nueva-version")
def crear_nueva_version(datos: DisenoCrear, sesion: Session = Depends(obtener_sesion)):
    predio_id = None
    if datos.predio_identificador:
        predio = sesion.query(Predio).filter_by(identificador=datos.predio_identificador).first()
        if not predio:
            raise HTTPException(404, f"Predio {datos.predio_identificador} no encontrado")
        predio_id = predio.id
    consulta = sesion.query(func.max(Diseno.version))
    if predio_id:
        consulta = consulta.filter_by(predio_id=predio_id)
    else:
        consulta = consulta.filter_by(predio_id=None).filter(Diseno.unidad_nombre == datos.unidad_nombre)
    max_version = consulta.scalar() or 0
    diseno = Diseno(
        predio_id=predio_id,
        unidad_nombre=datos.unidad_nombre,
        fecha=datos.fecha,
        version=max_version + 1,
        area_total_ha=datos.area_total_ha,
        zona_clima=datos.zona_clima,
        objetivo=datos.objetivo,
        tipo_diseno=datos.tipo_diseno,
        nivel_transicion=datos.nivel_transicion,
        usos_suelo=[u.model_dump() for u in datos.usos_suelo],
        componentes=[c.model_dump() for c in datos.componentes],
        rotacion_asociacion=datos.rotacion_asociacion,
        referencia_bibliografica=datos.referencia_bibliografica,
    )
    sesion.add(diseno)
    sesion.commit()
    sesion.refresh(diseno)
    return {"id": diseno.id, "version": diseno.version}


@enrutador.get("/{identificador}/historial")
def historial(identificador: str, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=identificador).first()
    if not predio:
        raise HTTPException(404, "Predio no encontrado")
    disenos = (
        sesion.query(Diseno).filter_by(predio_id=predio.id)
        .order_by(Diseno.version.desc()).all()
    )
    return [
        {"id": d.id, "version": d.version, "fecha": d.fecha, "unidad": d.unidad_nombre, "tipo": d.tipo_diseno}
        for d in disenos
    ]
