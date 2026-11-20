"""Tests SIG Fase 1: IGAC primero, precarga oficina->campo, pendiente guía."""
from fastapi.testclient import TestClient

from aplicacion.principal import app

cliente = TestClient(app)
BBOX = "-74.06,4.63,-74.03,4.66"


def test_listar_capas():
    r = cliente.get("/sig/capas")
    assert r.status_code == 200
    capas = {c["id"]: c for c in r.json()["capas"]}
    assert {"agrologia", "predial"} <= set(capas)
    # Cada capa debe venir de su propio servicio, nunca de la cartografía
    # básica de La Vega ni compartir la misma capa remota.
    assert "carto1000lavega" not in capas["agrologia"]["url_wms"]
    assert "carto1000lavega" not in capas["predial"]["url_wms"]
    assert capas["agrologia"]["url_wms"] != capas["predial"]["url_wms"]
    assert capas["agrologia"]["capa_remota"] != capas["predial"]["capa_remota"]


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
    agrologia = cliente.get("/sig/igac/mapa", params={"capa": "agrologia", "bbox": BBOX})
    predial = cliente.get("/sig/igac/mapa", params={"capa": "predial", "bbox": BBOX})
    assert agrologia.status_code == 200
    assert predial.status_code == 200
    url_agrologia = agrologia.json()["url_wms"]
    url_predial = predial.json()["url_wms"]
    assert "suelosdecolombiaaniveldeorden" in url_agrologia
    assert "Dato_Fundamental_Catastro" in url_predial
    assert "layers=0" in url_agrologia
    assert "layers=1" in url_predial
    assert "version=1.1.1" in url_agrologia and "srs=EPSG%3A4326" in url_agrologia
    assert "carto1000lavega" not in url_agrologia + url_predial


def test_rest_igac_por_capa_y_geojson():
    from aplicacion.servicios import sig_igac

    caja = sig_igac.validar_bbox(BBOX)
    url_agrologia = sig_igac.url_rest_getfeature("agrologia", caja)
    url_predial = sig_igac.url_rest_getfeature("predial", caja)
    assert "suelosdecolombiaaniveldeorden/MapServer/0/query" in url_agrologia
    assert "Dato_Fundamental_Catastro/MapServer/1/query" in url_predial
    assert "f=geojson" in url_agrologia and "f=geojson" in url_predial
    assert "carto1000lavega" not in url_agrologia + url_predial


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


def test_rusle_bosque_restaurado():
    r = cliente.get("/analisis/rusle", params={
        "predio_identificador": "a", "pendiente_pct": 12, "cobertura_pct": 60,
        "longitud_m": 50, "r": 3000, "k": 0.03, "practica": "bosque_restaurado",
    })
    assert r.status_code == 200
    assert r.json()["factores"]["p"] == 0.1


def test_enmienda_cal_requiere():
    r = cliente.get("/analisis/enmienda-cal", params={
        "predio_identificador": "a", "aluminio_cmol_kg": 2.0, "cice_cmol_kg": 8.0, "textura": "arcilloso",
    })
    assert r.status_code == 200
    cuerpo = r.json()
    # exceso = 2.0 - 20*8/100 = 0.4; dosis = 0.4*2.0 = 0.8
    assert cuerpo["dosis_t_ha"] == 0.8
    assert cuerpo["saturacion_al_pct"] == 25.0
    assert cuerpo["aplicaciones"] == 1
    assert "fuente" in cuerpo


def test_enmienda_cal_fracciona_dosis_alta():
    r = cliente.get("/analisis/enmienda-cal", params={
        "predio_identificador": "a", "aluminio_cmol_kg": 5.0, "cice_cmol_kg": 8.0, "textura": "arcilloso",
    })
    cuerpo = r.json()
    # exceso = 5.0-1.6 = 3.4; dosis = 6.8 -> 3 aplicaciones de 2.27
    assert cuerpo["dosis_t_ha"] == 6.8
    assert cuerpo["aplicaciones"] == 3
    assert cuerpo["dosis_por_aplicacion_t_ha"] <= 2.5


def test_enmienda_cal_no_requiere():
    r = cliente.get("/analisis/enmienda-cal", params={
        "predio_identificador": "a", "aluminio_cmol_kg": 0.5, "cice_cmol_kg": 10.0, "textura": "franco",
    })
    assert r.json()["clase"] == "no requiere"


def test_enmienda_cal_cice_invalida():
    r = cliente.get("/analisis/enmienda-cal", params={
        "predio_identificador": "a", "aluminio_cmol_kg": 1.0, "cice_cmol_kg": 0, "textura": "franco",
    })
    assert r.status_code in (400, 422)


def test_lluvia_ideam_demo():
    r = cliente.get("/analisis/lluvia-ideam", params={"municipio": "Mosquera", "modo": "demo"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["anual_mm"] == 985.0
    assert cuerpo["imf"] > 0
    assert "R sigue editable" in cuerpo["nota"]


def test_lluvia_ideam_sin_municipio_400():
    r = cliente.get("/analisis/lluvia-ideam", params={"municipio": "  ", "modo": "demo"})
    assert r.status_code == 400


def test_indice_fournier_matematica():
    from aplicacion.servicios import lluvia_ideam
    mensuales = [100.0] * 12
    assert lluvia_ideam.indice_fournier(mensuales) == 100.0


def test_upra_frontera_demo():
    r = cliente.get("/sig/upra-frontera", params={"municipio": "Mosquera", "modo": "demo"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total_ha"] == 12703.0
    assert "sipra.upra.gov.co" in cuerpo["aptitud_sipra"]
    assert "indicativo" in cuerpo["nota"]


def test_upra_frontera_sin_municipio_400():
    r = cliente.get("/sig/upra-frontera", params={"municipio": "  ", "modo": "demo"})
    assert r.status_code == 400


def test_dem_copernicus_tesela_y_url():
    from aplicacion.servicios import sig_dem

    assert sig_dem.nombre_tesela(4.645, -74.045) == "Copernicus_DSM_COG_10_N04_00_W075_00_DEM"
    assert sig_dem.nombre_tesela(-3.2, -70.4) == "Copernicus_DSM_COG_10_S04_00_W071_00_DEM"
    url = sig_dem.url_tesela(4.645, -74.045)
    assert url.endswith("Copernicus_DSM_COG_10_N04_00_W075_00_DEM/Copernicus_DSM_COG_10_N04_00_W075_00_DEM.tif")
    assert "copernicus-dem-30m" in url


def test_dem_copernicus_muestreo_real_sin_red(monkeypatch):
    from aplicacion.servicios import sig_dem

    monkeypatch.setattr(
        sig_dem,
        "_elevaciones_copernicus",
        lambda puntos: [2600.0, 2600.0, 2600.0, 2600.0, 2400.0, 2600.0, 2600.0, 2600.0, 2600.0],
    )
    estimado = sig_dem.muestrear_dem((-74.06, 4.63, -74.03, 4.66))
    assert 5 < estimado["pendiente_pct"] < 25
    assert estimado["resolucion_m"] == 30
    assert estimado["teselas"] == ["Copernicus_DSM_COG_10_N04_00_W075_00_DEM"]
    assert "Copernicus DEM GLO-30" in estimado["fuente"]


def test_ndvi_real_sin_credenciales_503(monkeypatch):
    from aplicacion.configuracion import configuracion

    monkeypatch.setattr(configuracion, "copernicus_id_cliente", None)
    monkeypatch.setattr(configuracion, "copernicus_secreto_cliente", None)
    r = cliente.get("/analisis/ndvi-serie", params={"predio_identificador": "a", "bbox": BBOX})
    assert r.status_code == 503
    assert "COPERNICUS" in r.json()["detail"]


def test_ndvi_cuerpo_estadisticas():
    from aplicacion.servicios import sig_ndvi

    cuerpo = sig_ndvi.cuerpo_estadisticas((-74.06, 4.63, -74.03, 4.66), "2026-04-01", "2026-10-01")
    assert cuerpo["input"]["bounds"]["bbox"] == [-74.06, 4.63, -74.03, 4.66]
    assert cuerpo["input"]["data"][0]["type"] == "sentinel-2-l2a"
    assert cuerpo["aggregation"]["aggregationInterval"] == {"of": "P30D"}
    assert "NDVI" not in cuerpo["aggregation"]["evalscript"]
    assert "B08" in cuerpo["aggregation"]["evalscript"]


def test_ndvi_serie_real_parsea(monkeypatch):
    import requests

    from aplicacion.configuracion import configuracion
    from aplicacion.servicios import sig_ndvi

    class Respuesta:
        def __init__(self, cuerpo):
            self._cuerpo = cuerpo

        def raise_for_status(self):
            return None

        def json(self):
            return self._cuerpo

    def post_falso(url, **kwargs):
        if "token" in url:
            return Respuesta({"access_token": "token-prueba"})
        return Respuesta(
            {
                "data": [
                    {
                        "interval": {"from": "2026-08-01T00:00:00Z", "to": "2026-08-31T00:00:00Z"},
                        "outputs": [
                            {
                                "bands": [
                                    {"stats": {"mean": 0.22, "sampleCount": 90}},
                                    {"stats": {"mean": 0.05, "sampleCount": 90}},
                                ]
                            }
                        ],
                    },
                    {
                        "interval": {"from": "2026-09-01T00:00:00Z", "to": "2026-09-30T00:00:00Z"},
                        "outputs": [
                            {
                                "bands": [
                                    {"stats": {"mean": 0.64, "sampleCount": 80}},
                                    {"stats": {"mean": 0.4, "sampleCount": 80}},
                                ]
                            }
                        ],
                    },
                ]
            }
        )

    monkeypatch.setattr(configuracion, "copernicus_id_cliente", "id")
    monkeypatch.setattr(configuracion, "copernicus_secreto_cliente", "secreto")
    monkeypatch.setattr(sig_ndvi.requests, "post", post_falso)
    resultado = sig_ndvi.serie_real((-74.06, 4.63, -74.03, 4.66))
    puntos = resultado["puntos"]
    assert [p["ndvi"] for p in puntos] == [0.22, 0.64]
    assert puntos[0]["clase"] == "suelo/estrés"
    assert puntos[1]["clase"] == "vigoroso"
    assert puntos[1]["nubosidad_pct"] == 40
    assert "Sentinel-2" in resultado["fuente"]
    assert sig_ndvi.interpretar_serie(puntos)["tendencia"] == "al alza"
