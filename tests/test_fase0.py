"""Tests Fase 0: modelos completos, auth JWT y extracción."""
import json
from pathlib import Path


def test_references_json_existe_y_tiene_16():
    refs = json.loads((Path(__file__).parents[1] / "datos_bibliograficos" / "references.json").read_text(encoding="utf-8"))
    assert len(refs) == 16
    cats = {r["categoria"] for r in refs}
    assert "soil_field_methods" in cats and "agroforestry" in cats


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
    assert "ph_agua" in {c.name for c in __import__("aplicacion.modelos.ficha_suelo", fromlist=["FichaSuelo"]).FichaSuelo.__table__.columns}


def test_auth_token():
    from aplicacion.rutas.auth import crear_token, SECRETO, ALGORITMO
    from jose import jwt
    t = crear_token("tecnico")
    assert jwt.decode(t, SECRETO, algorithms=[ALGORITMO])["sub"] == "tecnico"
