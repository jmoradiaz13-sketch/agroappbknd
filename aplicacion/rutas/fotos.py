"""Rutas de fotos: subida multipart offline-queue + descarga."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio
from ..modelos.ficha_suelo import FichaSuelo
from ..modelos.foto_muestra import FotoMuestra

enrutador = APIRouter(prefix="/fotos", tags=["fotos"])

TIPOS = {"muestra", "vess", "cobertura", "punto"}


@enrutador.post("")
def subir_foto(
    archivo: UploadFile = File(...),
    predio_identificador: str = Form(...),
    ficha_version: int | None = Form(default=None),
    lote_nombre: str | None = Form(default=None),
    tipo: str = Form(default="muestra"),
    lat: float | None = Form(default=None),
    lng: float | None = Form(default=None),
    cobertura_pct: float | None = Form(default=None),
    fecha: date | None = Form(default=None),
    sesion: Session = Depends(obtener_sesion),
):
    if tipo not in TIPOS:
        raise HTTPException(400, f"Tipo inválido (muestra|vess|cobertura|punto)")
    contenido = archivo.file.read()
    if len(contenido) > 5 * 1024 * 1024:
        raise HTTPException(400, "Foto mayor a 5 MB (comprimir en cliente)")
    ficha_id = None
    if ficha_version is not None:
        predio = sesion.query(Predio).filter_by(identificador=predio_identificador).first()
        if not predio:
            raise HTTPException(404, f"Predio {predio_identificador} no encontrado")
        ficha = sesion.query(FichaSuelo).filter_by(predio_id=predio.id, version=ficha_version).first()
        if not ficha:
            raise HTTPException(404, f"Ficha v{ficha_version} no encontrada")
        ficha_id = ficha.id
    foto = FotoMuestra(
        ficha_id=ficha_id,
        predio_identificador=predio_identificador,
        lote_nombre=lote_nombre,
        tipo=tipo,
        imagen=contenido,
        miniatura=None,
        lat=lat, lng=lng,
        cobertura_pct=cobertura_pct,
        fecha=fecha,
    )
    sesion.add(foto)
    sesion.commit()
    sesion.refresh(foto)
    return {"id": foto.id, "tipo": foto.tipo}


@enrutador.get("/por-ficha/{identificador}/{version}")
def listar_por_ficha(identificador: str, version: int, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=identificador).first()
    if not predio:
        raise HTTPException(404, "Predio no encontrado")
    ficha = sesion.query(FichaSuelo).filter_by(predio_id=predio.id, version=version).first()
    if not ficha:
        raise HTTPException(404, "Ficha no encontrada")
    fotos = sesion.query(FotoMuestra).filter_by(ficha_id=ficha.id).order_by(FotoMuestra.id).all()
    return [
        {"id": f.id, "tipo": f.tipo, "lat": f.lat, "lng": f.lng,
         "cobertura_pct": f.cobertura_pct, "fecha": f.fecha}
        for f in fotos
    ]


@enrutador.get("/{foto_id}/archivo")
def descargar_archivo(foto_id: int, sesion: Session = Depends(obtener_sesion)):
    foto = sesion.query(FotoMuestra).filter_by(id=foto_id).first()
    if not foto:
        raise HTTPException(404, "Foto no encontrada")
    return Response(content=bytes(foto.imagen), media_type="image/jpeg")
