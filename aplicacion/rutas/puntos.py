"""Rutas de puntos de muestreo: alta idempotente por código (Etapa 7)."""
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..base_datos import obtener_sesion
from ..modelos.punto_muestreo import PuntoMuestreo

enrutador = APIRouter(prefix="/puntos", tags=["puntos"])


@enrutador.post("")
def guardar_punto(
    predio_identificador: str,
    codigo: str,
    lat: float,
    lng: float,
    lote_nombre: str | None = None,
    fecha: date | None = None,
    sesion: Session = Depends(obtener_sesion),
):
    """Crea el punto o devuelve el existente si el código ya se sincronizó."""
    existente = sesion.query(PuntoMuestreo).filter_by(codigo=codigo.strip()).first()
    if existente:
        return {"id": existente.id, "codigo": existente.codigo, "repetido": True}
    punto = PuntoMuestreo(
        predio_identificador=predio_identificador.strip(),
        lote_nombre=lote_nombre,
        codigo=codigo.strip(),
        lat=lat,
        lng=lng,
        fecha=fecha,
    )
    sesion.add(punto)
    sesion.commit()
    sesion.refresh(punto)
    return {"id": punto.id, "codigo": punto.codigo, "repetido": False}


@enrutador.get("/por-predio/{identificador}")
def puntos_por_predio(identificador: str, sesion: Session = Depends(obtener_sesion)):
    puntos = (
        sesion.query(PuntoMuestreo)
        .filter_by(predio_identificador=identificador)
        .order_by(PuntoMuestreo.codigo)
        .all()
    )
    return [
        {"codigo": p.codigo, "lote_nombre": p.lote_nombre, "lat": p.lat, "lng": p.lng, "fecha": p.fecha}
        for p in puntos
    ]
