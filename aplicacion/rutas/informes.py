"""Rutas de informes PDF/HTML inmutables (generados desde ficha versionada)."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio
from ..modelos.ficha_suelo import FichaSuelo
from ..servicios.informe_pdf import informe_para_ficha
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
    html, pdf = informe_para_ficha(identificador, ficha.version, _ficha_a_valores(ficha))
    if pdf:
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": f"attachment; filename=informe-{identificador}-v{ficha.version}.pdf"})
    return HTMLResponse(content=html)
