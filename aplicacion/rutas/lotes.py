"""Rutas de lotes: subdivisión del predio (polígono 4326 -> 4686)."""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio
from ..modelos.lote import Lote
from .predios import area_ha_geography

enrutador = APIRouter(prefix="/lotes", tags=["lotes"])


@enrutador.post("")
def crear_lote(predio_identificador: str, nombre: str, geojson: dict,
               uso_actual: str | None = None, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=predio_identificador).first()
    if not predio:
        raise HTTPException(404, "Predio no encontrado")
    lote = Lote(predio_id=predio.id, nombre=nombre, uso_actual=uso_actual)
    sesion.add(lote)
    sesion.flush()
    sesion.execute(
        Lote.__table__.update().where(Lote.id == lote.id).values(
            geometria=func.ST_Transform(func.ST_GeomFromGeoJSON(f"SRID=4326;{json.dumps(geojson)}"), 4686))
    )
    sesion.flush()
    # Área métrica precisa con geography (AGENTS.md §2.4), en hectáreas
    area_ha = area_ha_geography(sesion, Lote, lote.id)
    if area_ha is not None:
        sesion.execute(
            Lote.__table__.update().where(Lote.id == lote.id).values(area_ha=area_ha)
        )
    sesion.commit()
    return {"id": lote.id, "nombre": nombre, "area_ha": area_ha}


@enrutador.get("/por-predio/{identificador}")
def lotes_por_predio(identificador: str, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=identificador).first()
    if not predio:
        raise HTTPException(404, "Predio no encontrado")
    lotes = sesion.query(Lote).filter_by(predio_id=predio.id).all()
    return [{"id": l.id, "nombre": l.nombre, "uso_actual": l.uso_actual, "area_ha": l.area_ha} for l in lotes]
