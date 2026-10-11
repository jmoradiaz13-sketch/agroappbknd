"""Tests SIG Fase 1: IGAC primero, precarga oficina->campo, pendiente guía."""
from fastapi.testclient import TestClient

from aplicacion.principal import app

cliente = TestClient(app)
BBOX = "-74.06,4.63,-74.03,4.66"


def test_listar_capas():
    r = cliente.get("/sig/capas")
    assert r.status_code == 200
    ids = {c["id"] for c in r.json()["capas"]}
    assert {"agrologia", "predial"} <= ids


def test_geojson_demo_sin_red():
    r = cliente.get("/sig/igac/geojson", params={"capa": "agrologia", "bbox": BBOX, "modo": "demo"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["geojson"]["type"] == "FeatureCollection"
    assert cuerpo["insignia"] == "MIXTO"


def test_geojson_capa_invalida():
    r = cliente.get("/sig/igac/geojson", params={"capa": "suelos_marte", "bbox": BBOX, "modo": "demo"})
    assert r.status_code == 400


def test_geojson_bbox_fuera_colombia():
    r = cliente.get("/sig/igac/geojson", params={"capa": "agrologia", "bbox": "0,0,1,1", "modo": "demo"})
    assert r.status_code == 400


def test_mapa_wms_construye_url():
    r = cliente.get("/sig/igac/mapa", params={"capa": "predial", "bbox": BBOX})
    assert r.status_code == 200
    assert "url_wms" in r.json()


def test_precarga_ok_y_cabe():
    r = cliente.post("/sig/precarga", json={"predio_identificador": "finca-mirador", "bbox": BBOX, "capas": ["agrologia", "predial"]})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["cabe_en_cache"] is True
    assert cuerpo["peso_total_mb"] <= 200


def test_precarga_bbox_invalido():
    r = cliente.post("/sig/precarga", json={"predio_identificador": "x", "bbox": "mal", "capas": ["agrologia"]})
    assert r.status_code == 400


def test_pendiente_clases():
    assert cliente.get("/analisis/pendiente-rusle", params={"predio_identificador": "a", "pendiente_pct": 5}).json()["clase"] == "plano"
    assert cliente.get("/analisis/pendiente-rusle", params={"predio_identificador": "a", "pendiente_pct": 12}).json()["clase"] == "ondulado"
    assert cliente.get("/analisis/pendiente-rusle", params={"predio_identificador": "a", "pendiente_pct": 40}).json()["clase"] == "empinado"
    guia = cliente.get("/analisis/pendiente-rusle", params={"predio_identificador": "a"}).json()
    assert "clases" in guia


def test_pendiente_dem_demo():
    r = cliente.get("/analisis/pendiente-dem", params={"predio_identificador": "a", "bbox": BBOX, "modo": "demo"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["clase"] == "ondulado"
    assert cuerpo["pendiente_pct"] == 12.4
    assert cuerpo["insignia"] == "MIXTO"


def test_pendiente_dem_bbox_invalido():
    r = cliente.get("/analisis/pendiente-dem", params={"predio_identificador": "a", "bbox": "mal", "modo": "demo"})
    assert r.status_code == 400


def test_dem_malla_y_calculo():
    from aplicacion.servicios import sig_dem
    puntos = sig_dem.malla_bbox((-74.06, 4.63, -74.03, 4.66))
    assert len(puntos) == 9
    # Desnivel 200 m en ~1,6 km -> ondulado ~12 %
    elevaciones = [2600.0, 2600.0, 2600.0, 2600.0, 2400.0, 2600.0, 2600.0, 2600.0, 2600.0]
    estimado = sig_dem.pendiente_desde_elevaciones(puntos, elevaciones)
    assert 5 < estimado["pendiente_pct"] < 25
    assert sig_dem.clasificar(estimado["pendiente_pct"])[0] == "ondulado"


def test_ndvi_serie_demo():
    r = cliente.get("/analisis/ndvi-serie", params={"predio_identificador": "a", "bbox": BBOX, "modo": "demo"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert len(cuerpo["puntos"]) == 3
    assert cuerpo["puntos"][-1]["clase"] == "suelo/estrés"
    assert cuerpo["interpretacion"]["tendencia"] == "a la baja"
    assert "Zona débil" in (cuerpo["interpretacion"]["alerta"] or "")


def test_ndvi_serie_bbox_invalido():
    r = cliente.get("/analisis/ndvi-serie", params={"predio_identificador": "a", "bbox": "mal", "modo": "demo"})
    assert r.status_code == 400


def test_ndvi_clases():
    from aplicacion.servicios import sig_ndvi
    assert sig_ndvi.clasificar_ndvi(0.2)[0] == "suelo/estrés"
    assert sig_ndvi.clasificar_ndvi(0.5)[0] == "transición"
    assert sig_ndvi.clasificar_ndvi(0.7)[0] == "vigoroso"


def test_rusle_calculo():
    r = cliente.get("/analisis/rusle", params={
        "predio_identificador": "a", "pendiente_pct": 12, "cobertura_pct": 60,
        "longitud_m": 50, "r": 3000, "k": 0.03, "practica": "sin_practicas",
    })
    assert r.status_code == 200
    cuerpo = r.json()
    assert 40 < cuerpo["perdida_t_ha_ano"] < 65
    assert cuerpo["clase"] == "alta"
    assert cuerpo["factores"]["ls"] > 2


def test_rusle_cobertura_baja_riesgo():
    r = cliente.get("/analisis/rusle", params={
        "predio_identificador": "a", "pendiente_pct": 3, "cobertura_pct": 90,
        "longitud_m": 30, "r": 3000, "k": 0.03, "practica": "curvas_nivel",
    })
    assert r.json()["clase"] == "leve"


def test_rusle_practica_invalida():
    r = cliente.get("/analisis/rusle", params={"predio_identificador": "a", "pendiente_pct": 10, "practica": "magia"})
    assert r.status_code == 422
