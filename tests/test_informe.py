"""Tests Fase 3: informe HTML/PDF trazable (sin DB, sin GTK obligatorio)."""
from aplicacion.servicios.informe_pdf import informe_para_ficha


def test_informe_contiene_porque_y_fuente():
    html, _pdf = informe_para_ficha("predio-demo-001", 1, {
        "materia_organica_pct": 1.2, "fosforo_mg_kg": 10.0,
        "potasio_cmol_kg": 0.3, "calcio_cmol_kg": 5.0,
        "magnesio_cmol_kg": 1.0, "conductividad_ds_m": 0.5,
        "nitrogeno_pct": 0.15,
    })
    assert "predio-demo-001" in html
    assert "Por qu" in html or "porque" in html.lower() or "Por qué" in html
    assert ".pdf" in html
    assert "cmol/kg" in html
