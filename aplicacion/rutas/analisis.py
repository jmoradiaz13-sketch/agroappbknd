"""Análisis espacial MIXTO/ONLINE: DEM→pendiente/RUSLE, IGAC, NDVI (MVP manual)."""
from fastapi import APIRouter

enrutador = APIRouter(prefix="/analisis", tags=["analisis"])


@enrutador.get("/pendiente-rusle")
def pendiente_rusle(predio_identificador: str):
    # TODO: descargar DEM inicial, calcular pendiente con richdem/rasterio,
    # cachear GeoTIFF en Dexie (frontend). Requiere conexión inicial.
    return {
        "predio": predio_identificador,
        "estado": "pendiente de DEM inicial (MIXTO)",
        "nota": "Implementar con rasterio+richdem según determinacion_de_zonas_homogeneas_de_cultivo_agricultura_precision.pdf"
    }


@enrutador.get("/salud")
def salud():
    return {"estado": "ok", "srid_almacenamiento": 4686, "srid_cliente": 4326}
