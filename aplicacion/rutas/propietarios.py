"""Rutas de propietarios: un registro mutable por predio (Etapa 1)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio
from ..modelos.propietario import Propietario

enrutador = APIRouter(prefix="/propietarios", tags=["propietarios"])

TENENCIAS = {"propiedad", "arrendamiento", "sucesion", "otro"}
VOCACIONES = {"cafe", "ganaderia", "cacao", "policultivo", "otro"}


class PropietarioEntrada(BaseModel):
    predio_identificador: str
    nombre_completo: str
    cedula: str | None = None
    contacto: str | None = None
    tenencia: str | None = None
    vocacion: str | None = None
    mano_obra_familiar: int | None = None


def _validar(entrada: PropietarioEntrada) -> None:
    if not entrada.nombre_completo.strip():
        raise HTTPException(400, "El nombre del propietario es obligatorio")
    if entrada.tenencia is not None and entrada.tenencia not in TENENCIAS:
        raise HTTPException(400, f"Tenencia no válida. Usa: {sorted(TENENCIAS)}")
    if entrada.vocacion is not None and entrada.vocacion not in VOCACIONES:
        raise HTTPException(400, f"Vocación no válida. Usa: {sorted(VOCACIONES)}")
    if entrada.mano_obra_familiar is not None and entrada.mano_obra_familiar < 0:
        raise HTTPException(400, "La mano de obra familiar no puede ser negativa")


@enrutador.post("")
def guardar_propietario(entrada: PropietarioEntrada, sesion: Session = Depends(obtener_sesion)):
    """Crea o actualiza el propietario del predio (dato mutable de gestión)."""
    _validar(entrada)
    predio = sesion.query(Predio).filter_by(identificador=entrada.predio_identificador).first()
    if not predio:
        raise HTTPException(404, "Predio no encontrado")
    propietario = sesion.query(Propietario).filter_by(predio_id=predio.id).first()
    datos = {
        "nombre_completo": entrada.nombre_completo.strip(),
        "cedula": entrada.cedula,
        "contacto": entrada.contacto,
        "tenencia": entrada.tenencia,
        "vocacion": entrada.vocacion,
        "mano_obra_familiar": entrada.mano_obra_familiar,
    }
    if propietario is None:
        propietario = Propietario(predio_id=predio.id, **datos)
        sesion.add(propietario)
    else:
        for campo, valor in datos.items():
            setattr(propietario, campo, valor)
    sesion.commit()
    sesion.refresh(propietario)
    return {"id": propietario.id, "predio": predio.identificador}


@enrutador.get("/por-predio/{identificador}")
def propietario_por_predio(identificador: str, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=identificador).first()
    if not predio:
        raise HTTPException(404, "Predio no encontrado")
    propietario = sesion.query(Propietario).filter_by(predio_id=predio.id).first()
    if not propietario:
        return {"predio": identificador, "propietario": None}
    return {
        "predio": identificador,
        "propietario": {
            "nombre_completo": propietario.nombre_completo,
            "cedula": propietario.cedula,
            "contacto": propietario.contacto,
            "tenencia": propietario.tenencia,
            "vocacion": propietario.vocacion,
            "mano_obra_familiar": propietario.mano_obra_familiar,
        },
    }
