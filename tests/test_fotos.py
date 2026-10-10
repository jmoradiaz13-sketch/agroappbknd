"""Fotos offline: modelo versionado y rutas cableadas (sin DB en tests)."""


def test_modelo_foto_existe():
    from aplicacion.modelos.foto_muestra import FotoMuestra
    columnas = {c.name for c in FotoMuestra.__table__.columns}
    assert FotoMuestra.__tablename__ == "fotos_muestra"
    assert {"predio_identificador", "tipo", "imagen", "fecha"} <= columnas


def test_rutas_fotos_registradas():
    from aplicacion.rutas.fotos import enrutador
    rutas = {(r.path, next(iter(r.methods))) for r in enrutador.routes}
    assert ("/fotos", "POST") in rutas
    assert ("/fotos/por-ficha/{identificador}/{version}", "GET") in rutas
    assert ("/fotos/{foto_id}/archivo", "GET") in rutas


def test_tipos_validos():
    from aplicacion.rutas.fotos import TIPOS
    assert TIPOS == {"muestra", "vess", "cobertura", "punto"}
