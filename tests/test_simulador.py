"""Tests del simulador: compatibilidad citada, escenarios A/B/C y proyección."""
from fastapi.testclient import TestClient

from aplicacion.principal import app
from aplicacion.servicios import simulador

cliente = TestClient(app)

CACAO = {
    "nombre_comun": "Cacao", "rol": "Frutal / ingreso",
    "ph_min": 5.5, "ph_max": 7.0, "mo_min_pct": 3,
    "texturas": ["franco"], "pendiente_max_pct": 25, "zona_vida": "todas",
}
SITIO = {"ph": 6.0, "mo_pct": 4.0, "textura": "franco", "pendiente_pct": 12.0, "zona_vida": "bh-MB"}


def test_compatibilidad_apta_con_cita():
    r = cliente.post("/simulador/compatibilidad", json={"especie": CACAO, "sitio": SITIO})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["apta"] is True
    assert cuerpo["puntaje"] >= 50
    assert all("cita" in m for m in cuerpo["motivos"])


def test_descarte_pendiente_documentado():
    r = cliente.post("/simulador/compatibilidad", json={
        "especie": CACAO, "sitio": {**SITIO, "pendiente_pct": 40.0},
    })
    cuerpo = r.json()
    assert cuerpo["apta"] is False
    assert cuerpo["puntaje"] == 0
    assert "restauración" in cuerpo["motivos"][0]["regla"]


def test_descarte_ph_documentado():
    r = cliente.post("/simulador/compatibilidad", json={
        "especie": CACAO, "sitio": {**SITIO, "ph": 4.0},
    })
    assert r.json()["apta"] is False


def test_escenarios_tres_con_rusle():
    r = cliente.post("/simulador/escenarios", json={"sitio": SITIO, "especies": [CACAO]})
    assert r.status_code == 200
    escenarios = r.json()["escenarios"]
    assert [e["tipo"] for e in escenarios] == ["A", "B", "C"]
    for e in escenarios:
        assert e["rusle_despues_t_ha_ano"] <= e["rusle_antes_t_ha_ano"]
        assert sum(e["usos"].values()) == 100
    b = [e for e in escenarios if e["tipo"] == "B"][0]
    assert b["conservacion_pct"] >= 10


def test_escenarios_sin_pendiente_400():
    r = cliente.post("/simulador/escenarios", json={"sitio": {"ph": 6.0}, "especies": []})
    assert r.status_code == 400


def test_proyeccion_creciente():
    r = cliente.post("/simulador/proyeccion", params={"cobertura_inicial": 40.0, "anos": 5})
    serie = r.json()["serie"]
    assert len(serie) == 6
    valores = [p["cobertura_pct"] for p in serie]
    assert valores == sorted(valores)
    assert valores[-1] > 85


def test_proyeccion_invalida_400():
    assert cliente.post("/simulador/proyeccion", params={"cobertura_inicial": 0}).status_code == 400
    assert simulador.proyeccion_cobertura(40.0)[0]["cobertura_pct"] == 40.0


def test_costos_escenario_a():
    r = cliente.post("/simulador/costos", params={"tipo": "A", "area_ha": 2.0})
    assert r.status_code == 200
    cuerpo = r.json()
    # establecimiento 2*(40*60000+1200000)=7.2M + mant 2*800000*5=8M
    assert cuerpo["total_cop"] == 15200000.0
    assert cuerpo["costo_ha_cop"] == 7600000.0
    assert len(cuerpo["supuestos"]) == 3


def test_costos_b_mas_barato_que_a():
    a = cliente.post("/simulador/costos", params={"tipo": "A", "area_ha": 1.0}).json()
    b = cliente.post("/simulador/costos", params={"tipo": "B", "area_ha": 1.0}).json()
    assert b["total_cop"] < a["total_cop"]


def test_costos_tipo_invalido_400():
    assert cliente.post("/simulador/costos", params={"tipo": "Z", "area_ha": 1.0}).status_code == 400
    assert cliente.post("/simulador/costos", params={"tipo": "A", "area_ha": 0}).status_code == 400


def test_rotaciones_precargadas():
    r = cliente.get("/simulador/rotaciones")
    assert r.status_code == 200
    rotaciones = r.json()["rotaciones"]
    assert len(rotaciones) >= 4
    for rot in rotaciones:
        assert len(rot["secuencia"]) >= 3
        assert "fuente" in rot and rot["fuente"]


def test_riego_con_hargreaves():
    r = cliente.post("/simulador/riego", params={
        "cultivo": "cacao", "lluvia_mm": 2.0, "tmax": 30.0, "tmin": 20.0,
    })
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["eto_mm"] > 0
    assert cuerpo["lamina_riego_mm"] >= 0
    assert cuerpo["kc"] == 1.05


def test_riego_sin_riego_con_lluvia():
    r = cliente.post("/simulador/riego", params={
        "cultivo": "yuca", "lluvia_mm": 20.0, "eto_mm": 4.0,
    })
    assert r.json()["lamina_riego_mm"] == 0.0


def test_riego_cultivo_invalido_400():
    assert cliente.post("/simulador/riego", params={"cultivo": "marte", "lluvia_mm": 1}).status_code == 400
    assert cliente.post("/simulador/riego", params={"cultivo": "cacao", "lluvia_mm": -1}).status_code == 400
