"""Rutas de referencias bibliográficas + monitoreo."""
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..base_datos import obtener_sesion
from ..modelos.referencia import ReferenciaBibliografica
from ..modelos.monitoreo import Monitoreo

enrutador_ref = APIRouter(prefix="/referencias", tags=["referencias"])
enrutador_mon = APIRouter(prefix="/monitoreos", tags=["monitoreos"])


@enrutador_ref.get("")
def listar_referencias(sesion: Session = Depends(obtener_sesion)):
    refs = sesion.query(ReferenciaBibliografica).limit(100).all()
    return [{"id": r.id, "titulo": r.titulo, "fuente": r.fuente, "uso": r.uso_en_proyecto} for r in refs]


@enrutador_mon.post("")
def crear_monitoreo(lote_id: int, indicadores: dict, observaciones: str | None = None,
                    sesion: Session = Depends(obtener_sesion)):
    mon = Monitoreo(lote_id=lote_id, fecha=date.today(), indicadores=indicadores, observaciones=observaciones)
    sesion.add(mon)
    sesion.commit()
    sesion.refresh(mon)
    return {"id": mon.id}


@enrutador_mon.get("/por-lote/{lote_id}")
def monitoreos_por_lote(lote_id: int, sesion: Session = Depends(obtener_sesion)):
    mons = sesion.query(Monitoreo).filter_by(lote_id=lote_id).order_by(Monitoreo.fecha.desc()).all()
    return [{"id": m.id, "fecha": m.fecha, "indicadores": m.indicadores} for m in mons]
