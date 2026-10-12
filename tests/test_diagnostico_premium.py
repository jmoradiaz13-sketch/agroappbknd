"""Tests premium diagnóstico: puntaje salud + nivel riesgo RUSLE (sin romper clases)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aplicacion.servicios.motor_diagnostico import diagnosticar, puntaje_salud
from aplicacion.servicios import sig_rusle


def test_puntaje_salud_trazable():
    hallazgos = diagnosticar({
        "materia_organica_pct": 4.0,
        "fosforo_mg_kg": 20.0,
        "potasio_cmol_kg": 0.3,
        "calcio_cmol_kg": 5.0,
        "magnesio_cmol_kg": 1.0,
        "conductividad_ds_m": 0.5,
        "nitrogeno_pct": 0.15,
    })
    puntaje = puntaje_salud(hallazgos)
    assert puntaje["puntaje"] == 90
    assert puntaje["nivel"] == "bueno"
    assert puntaje["n_total"] == 7
    assert ".pdf" in puntaje["fuente"]


def test_puntaje_pobre_con_deficiencias():
    hallazgos = diagnosticar({"materia_organica_pct": 1.0, "fosforo_mg_kg": 5.0})
    puntaje = puntaje_salud(hallazgos)
    assert puntaje["puntaje"] == 40
    assert puntaje["nivel"] == "pobre"


def test_puntaje_sin_datos():
    puntaje = puntaje_salud([])
    assert puntaje["puntaje"] == 0
    assert puntaje["nivel"] == "sin-datos"


def test_nivel_riesgo_plan_maestro():
    assert sig_rusle.nivel_riesgo(3.0) == ("bajo", "verde")
    assert sig_rusle.nivel_riesgo(10.0) == ("moderado", "amarillo")
    assert sig_rusle.nivel_riesgo(30.0) == ("severo", "naranja")
    assert sig_rusle.nivel_riesgo(80.0) == ("critico", "rojo")


def test_estimar_mantiene_clase_y_agrega_nivel():
    resultado = sig_rusle.estimar(3000, 0.03, 12, 50, 60, "sin_practicas")
    assert resultado["clase"] in ("leve", "moderada", "alta", "muy alta")
    assert resultado["nivel_riesgo"] in ("bajo", "moderado", "severo", "critico")
    assert "semaforo" in resultado
    assert "guardian_erosion" in resultado
    assert ".pdf" not in resultado["fuente"] or "VSA" in resultado["fuente"]
