"""Ficha extendida: el esquema acepta el panel completo y el motor
solo interpreta parámetros con rango validado (ignora el resto)."""
from aplicacion.esquemas.ficha import FichaSueloCrear
from aplicacion.servicios.motor_diagnostico import diagnosticar


def test_esquema_acepta_panel_extendido():
    ficha = FichaSueloCrear(
        predio_identificador="finca-demo",
        fecha="2026-01-15",
        tipo_evaluacion="mixta",
        clima_reciente="Lluvias moderadas la última semana",
        textura_tacto="franco",
        ph_campo=6.1,
        azufre_mg_kg=12.5,
        aluminio_cmol_kg=0.4,
        lombrices_conteo=85,
        respiracion_suelo=42.0,
        referencia_bibliografica="src/guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.12",
    )
    assert ficha.textura_tacto == "franco"
    assert ficha.lombrices_conteo == 85


def test_ficha_fisica_vess_munsell():
    ficha = FichaSueloCrear(
        predio_identificador="finca-demo",
        fecha="2026-01-15",
        tipo_evaluacion="campo",
        estructura_vess=2,
        munsell_h="10YR",
        munsell_v=3.0,
        munsell_c=2.0,
        color_estado="humedo",
        densidad_aparente=1.25,
        referencia_bibliografica="src/visual_soil_assessment.pdf",
    )
    assert ficha.estructura_vess == 2
    assert ficha.munsell_h == "10YR"


def test_motor_ignora_parametros_sin_rango():
    hallazgos = diagnosticar({"ph_campo": 6.1, "azufre_mg_kg": 12.5, "materia_organica_pct": 1.5})
    parametros = [h["parametro"] for h in hallazgos]
    assert "ph_campo" not in parametros
    assert "azufre_mg_kg" not in parametros
    assert "materia_organica_pct" in parametros
    assert hallazgos[0]["estado"] == "deficiente"


def test_sitio_muestreo_acepta_y_valida():
    import pytest
    from pydantic import ValidationError

    ficha = FichaSueloCrear(
        predio_identificador="finca-demo",
        fecha="2026-01-15",
        latitud=4.711,
        longitud=-74.072,
        precision_m=8.0,
        msnm=1650.0,
        pendiente_sitio_pct=12.0,
        posicion_relieve="ladera",
        uso_actual="cafetal",
        solicitante="Productor demo",
        tenencia_sitio="propietario",
        manejo_reciente="Fertilización hace 3 meses",
        vereda="El Mirador",
        municipio="Tibasosa",
        departamento="Boyacá",
    )
    assert ficha.uso_actual == "cafetal"
    assert ficha.posicion_relieve == "ladera"
    with pytest.raises(ValidationError):
        FichaSueloCrear(
            predio_identificador="finca-demo",
            fecha="2026-01-15",
            latitud=95.0,
        )
    with pytest.raises(ValidationError):
        FichaSueloCrear(
            predio_identificador="finca-demo",
            fecha="2026-01-15",
            posicion_relieve="cima_extrana",
        )
