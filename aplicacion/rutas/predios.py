"""Rutas de predios: recibe GeoJSON en EPSG:4326, almacena en EPSG:4686."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio

enrutador = APIRouter(prefix="/predios", tags=["predios"])


@enrutador.post("")
def crear_predio(identificador: str, nombre: str, geojson: dict, sesion: Session = Depends(obtener_sesion)):
    import json
    geometria_4326 = f"SRID=4326;{json.dumps(geojson)}"  # GeoJSON cliente
    predio = Predio(identificador=identificador, nombre=nombre)
    sesion.add(predio)
    sesion.flush()
    # Transforma a MAGNA-SIRGAS en DB
    sesion.execute(
        Predio.__table__.update()
        .where(Predio.id == predio.id)
        .values(geometria=func.ST_Transform(func.ST_GeomFromGeoJSON(geometria_4326), 4686))
    )
    sesion.commit()
    return {"id": predio.id, "identificador": identificador}


@enrutador.get("/{identificador}")
def obtener_predio(identificador: str, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=identificador).first()
    if not predio:
        return {"error": "no encontrado"}
    # Devuelve en EPSG:4326 para Leaflet
    geojson_4326 = sesion.scalar(func.ST_AsGeoJSON(func.ST_Transform(predio.geometria, 4326)))
    return {"identificador": predio.identificador, "nombre": predio.nombre, "geometria": geojson_4326}
