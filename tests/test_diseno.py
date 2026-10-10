"""Simulador de diseño: el esquema acepta diseños desde cero y la
referencia bibliográfica es opcional (se cuadra después)."""
from aplicacion.esquemas.diseno import DisenoCrear


def test_diseno_desde_cero_sin_referencia():
    diseno = DisenoCrear(
        unidad_nombre="Unidad demostrativa 5 ha",
        fecha="2026-01-15",
        area_total_ha=5.0,
        tipo_diseno="SAF",
        nivel_transicion=3,
        usos_suelo=[
            {"uso": "Cultivos", "porcentaje": 50},
            {"uso": "SAF", "porcentaje": 30},
            {"uso": "Conservación", "porcentaje": 20},
        ],
        componentes=[{"rol": "Sombrío", "especie": "Guamo (demostrativa)"}],
    )
    assert diseno.predio_identificador is None
    assert diseno.referencia_bibliografica is None
    assert sum(u.porcentaje for u in diseno.usos_suelo) == 100


def test_diseno_con_predio_y_referencia():
    diseno = DisenoCrear(
        predio_identificador="finca-mirador",
        unidad_nombre="Lote Café",
        fecha="2026-01-15",
        referencia_bibliografica="guía SAF Orinoquía (fuente registrada)",
    )
    assert diseno.predio_identificador == "finca-mirador"
