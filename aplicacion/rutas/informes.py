"""Rutas de informes PDF/HTML inmutables (generados desde ficha versionada)."""
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio
from ..modelos.ficha_suelo import FichaSuelo
from ..modelos.lote import Lote
from ..modelos.punto_muestreo import PuntoMuestreo
from ..servicios.informe_pdf import informe_para_ficha
from ..servicios.mapa_informe import croquis_svg
from ..rutas.diagnostico import _ficha_a_valores

enrutador = APIRouter(prefix="/informes", tags=["informes"])


@enrutador.get("/{identificador}/pdf")
def descargar_informe(identificador: str, version: int | None = None, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=identificador).first()
    if not predio:
        raise HTTPException(404, "Predio no encontrado")
    consulta = sesion.query(FichaSuelo).filter_by(predio_id=predio.id)
    ficha = consulta.filter_by(version=version).first() if version else consulta.order_by(FichaSuelo.version.desc()).first()
    if not ficha:
        raise HTTPException(404, "Sin ficha para generar informe")
    lotes = sesion.query(Lote).filter_by(predio_id=predio.id).all()
    geometrias = []
    for lote in lotes:
        geojson = sesion.scalar(func.ST_AsGeoJSON(func.ST_Transform(lote.geometria, 4326)))
        if geojson:
            geometrias.append({"nombre": lote.nombre, "geojson": json.loads(geojson)})
    puntos = sesion.query(PuntoMuestreo).filter_by(predio_identificador=identificador).all()
    mapa = croquis_svg(
        geometrias,
        [{"codigo": p.codigo, "lat": p.lat, "lng": p.lng} for p in puntos],
    )
    html, pdf = informe_para_ficha(identificador, ficha.version, _ficha_a_valores(ficha), mapa)
    if pdf:
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": f"attachment; filename=informe-{identificador}-v{ficha.version}.pdf"})
    return HTMLResponse(content=html)
