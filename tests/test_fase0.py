"""Tests Fase 0: modelos completos y auth JWT."""
def test_modelos_importan():
    from aplicacion.modelos.predio import Predio
    from aplicacion.modelos.lote import Lote
    from aplicacion.modelos.referencia import ReferenciaBibliografica
    from aplicacion.modelos.monitoreo import Monitoreo
    from aplicacion.modelos.estrategia import Estrategia
    assert Predio.__tablename__ == "predios"
    assert Lote.__tablename__ == "lotes"
    assert "propietario" in {c.name for c in Predio.__table__.columns}
    assert "uso_actual" in {c.name for c in Lote.__table__.columns}
    ficha = __import__("aplicacion.modelos.ficha_suelo", fromlist=["FichaSuelo"]).FichaSuelo
    assert "ph_agua" in {c.name for c in ficha.__table__.columns}
    assert "lote_id" in {c.name for c in ficha.__table__.columns}
    assert ficha.__table__.columns.referencia_bibliografica.nullable is True


def test_auth_token():
    from aplicacion.rutas.auth import crear_token, SECRETO, ALGORITMO
    from jose import jwt
    t = crear_token("tecnico")
    assert jwt.decode(t, SECRETO, algorithms=[ALGORITMO])["sub"] == "tecnico"
