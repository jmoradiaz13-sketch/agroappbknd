"""Prueba de unidades de almacenamiento (sin DB)."""
from aplicacion.esquemas.ficha import FichaSueloCrear
from datetime import date


def test_unidades_validas():
    ficha = FichaSueloCrear(
        predio_identificador="predio-demo-001",
        fecha=date(2026, 10, 7),
        calcio_cmol_kg=5.2,
        fosforo_mg_kg=12.5,
        materia_organica_pct=3.1,
        conductividad_ds_m=0.8,
        referencia_bibliografica="guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.12",
    )
    assert ficha.calcio_cmol_kg == 5.2
