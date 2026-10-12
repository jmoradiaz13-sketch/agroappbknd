"""Tests de puntos de muestreo: modelo y rutas registradas (sin DB)."""


def test_modelo_importa():
    from aplicacion.modelos.punto_muestreo import PuntoMuestreo
    columnas = {c.name for c in PuntoMuestreo.__table__.columns}
    assert PuntoMuestreo.__tablename__ == "puntos_muestreo"
    for campo in ("predio_identificador", "codigo", "lat", "lng", "fecha"):
        assert campo in columnas


def test_rutas_registradas():
    from aplicacion.principal import app
    rutas = {r.path for r in app.routes}
    assert "/puntos" in rutas
    assert "/puntos/por-predio/{identificador}" in rutas
