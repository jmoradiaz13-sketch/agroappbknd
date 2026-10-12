"""Tests de propietarios: modelo y validaciones (sin DB)."""
import pytest


def test_modelo_importa_con_campos():
    from aplicacion.modelos.propietario import Propietario
    columnas = {c.name for c in Propietario.__table__.columns}
    assert Propietario.__tablename__ == "propietarios"
    for campo in ("predio_id", "nombre_completo", "cedula", "tenencia", "vocacion", "mano_obra_familiar"):
        assert campo in columnas


def test_validar_nombre_obligatorio():
    from fastapi import HTTPException
    from aplicacion.rutas.propietarios import PropietarioEntrada, _validar
    with pytest.raises(HTTPException):
        _validar(PropietarioEntrada(predio_identificador="a", nombre_completo="  "))


def test_validar_tenencia_y_vocacion():
    from fastapi import HTTPException
    from aplicacion.rutas.propietarios import PropietarioEntrada, _validar
    with pytest.raises(HTTPException):
        _validar(PropietarioEntrada(predio_identificador="a", nombre_completo="X", tenencia="invasion"))
    with pytest.raises(HTTPException):
        _validar(PropietarioEntrada(predio_identificador="a", nombre_completo="X", vocacion="soya"))
    with pytest.raises(HTTPException):
        _validar(PropietarioEntrada(predio_identificador="a", nombre_completo="X", mano_obra_familiar=-1))
    # Válido no lanza
    _validar(PropietarioEntrada(
        predio_identificador="a", nombre_completo="María",
        tenencia="propiedad", vocacion="cacao", mano_obra_familiar=3,
    ))


def test_router_registrado():
    from aplicacion.principal import app
    rutas = {r.path for r in app.routes}
    assert "/propietarios" in rutas
