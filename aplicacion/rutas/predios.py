"""Rutas de predios: recibe GeoJSON en EPSG:4326, almacena en EPSG:4686."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import cast, func, select
from geoalchemy2 import Geography
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio

enrutador = APIRouter(prefix="/predios", tags=["predios"])


def area_ha_geography(sesion: Session, modelo, registro_id: int) -> float | None:
    """Área métrica precisa con ST_Area sobre geography (AGENTS.md §2.4)."""
    metros2 = sesion.scalar(
        select(func.ST_Area(cast(func.ST_Transform(modelo.geometria, 4326), Geography))).where(
            modelo.id == registro_id
        )
    )
    return round(float(metros2) / 10000, 2) if metros2 is not None else None


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
    sesion.flush()
    # Área métrica precisa con geography (AGENTS.md §2.4), en hectáreas
    area_ha = area_ha_geography(sesion, Predio, predio.id)
    if area_ha is not None:
        sesion.execute(
            Predio.__table__.update().where(Predio.id == predio.id).values(area_total_ha=area_ha)
        )
    sesion.commit()
    return {"id": predio.id, "identificador": identificador, "area_ha": area_ha}


@enrutador.get("/{identificador}")
def obtener_predio(identificador: str, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=identificador).first()
    if not predio:
        return {"error": "no encontrado"}
    # Devuelve en EPSG:4326 para Leaflet + área precisa en hectáreas
    geojson_4326 = sesion.scalar(func.ST_AsGeoJSON(func.ST_Transform(predio.geometria, 4326)))
    area_ha = predio.area_total_ha
    if area_ha is None:
        area_ha = area_ha_geography(sesion, Predio, predio.id)
    return {"identificador": predio.identificador, "nombre": predio.nombre, "geometria": geojson_4326, "area_ha": area_ha}
