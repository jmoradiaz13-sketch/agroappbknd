"""Tests Fase 1: motor diagnóstico trazable (sin DB)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aplicacion.servicios.motor_diagnostico import diagnosticar
from aplicacion.datos.referencias import CATALOGO_RANGOS


def test_todo_hallazgo_tiene_referencia():
    hallazgos = diagnosticar({
        "materia_organica_pct": 1.2,
        "fosforo_mg_kg": 50.0,
        "potasio_cmol_kg": 0.3,
        "calcio_cmol_kg": 5.0,
        "magnesio_cmol_kg": 1.0,
        "conductividad_ds_m": 0.5,
        "nitrogeno_pct": 0.15,
    })
    assert len(hallazgos) == 7
    for h in hallazgos:
        assert h["referencia_bibliografica"].endswith(".pdf p.12-18") or ".pdf" in h["referencia_bibliografica"]
        assert len(h["porque"]) > 20


def test_deficiente_y_exceso():
    h = {x["parametro"]: x for x in diagnosticar({"materia_organica_pct": 1.0})}
    assert h["materia_organica_pct"]["estado"] == "deficiente"
    h2 = {x["parametro"]: x for x in diagnosticar({"conductividad_ds_m": 5.0})}
    assert h2["conductividad_ds_m"]["estado"] == "exceso"


def test_catalogo_trazable():
    assert len(CATALOGO_RANGOS) >= 7
    for r in CATALOGO_RANGOS:
        assert r.fuente.endswith(".pdf cap. fertilidad") or ".pdf" in r.fuente


def test_relaciones_cationicas_matematicas():
    from aplicacion.servicios.motor_diagnostico import relaciones_cationicas
    rel = relaciones_cationicas({
        "calcio_cmol_kg": 6.0, "magnesio_cmol_kg": 2.0,
        "potasio_cmol_kg": 0.5, "aluminio_cmol_kg": 1.0,
    })
    assert rel["ca_mg"] == 3.0
    assert rel["mg_k"] == 4.0
    assert rel["ca_mg_k"] == 16.0
    assert rel["ca_al"] == 6.0
    incompleta = relaciones_cationicas({"calcio_cmol_kg": 6.0})
    assert incompleta["ca_mg"] is None and incompleta["mg_k"] is None


def test_ficha_sin_sodio_duplicado_y_con_nuevos():
    from aplicacion.modelos.ficha_suelo import FichaSuelo
    columnas = [c.name for c in FichaSuelo.__table__.columns]
    assert columnas.count("sodio_cmol_kg") == 1
    assert "densidad_real" in columnas and "metodo_fosforo" in columnas
