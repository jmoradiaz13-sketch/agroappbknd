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


def test_croquis_svg_con_lotes_y_puntos():
    from aplicacion.servicios.mapa_informe import croquis_svg
    svg = croquis_svg(
        [{"nombre": "Lote 1", "geojson": {
            "type": "Polygon",
            "coordinates": [[[-74.06, 4.64], [-74.04, 4.64], [-74.04, 4.66], [-74.06, 4.66], [-74.06, 4.64]]],
        }}],
        [{"codigo": "MU-001", "lat": 4.65, "lng": -74.05}],
    )
    assert "<svg" in svg and "Lote 1" in svg and "MU-001" in svg
    assert "no oficial" in svg


def test_croquis_sin_geometrias_avisa():
    from aplicacion.servicios.mapa_informe import croquis_svg
    assert "Sin geometrías" in croquis_svg([], [])


def test_informe_incluye_croquis():
    from aplicacion.servicios.informe_pdf import informe_para_ficha
    html, _pdf = informe_para_ficha("p-1", 2, {"ph_agua": 6.0}, "<svg>CROQUIS</svg>")
    assert "Croquis del predio" in html and "CROQUIS" in html
