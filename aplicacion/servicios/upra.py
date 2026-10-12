"""Frontera agrícola UPRA (datos tabulares, sin geometría predial).

Fuente: UPRA en datos.gov.co (recurso fyc7-sbtz, 1:100.000): porción del
municipio dentro de frontera (No condicionada) y condicionada. La aptitud
A1/A2/A3 por cultivo se consulta en SIPRA (Esri, sin API abierta): se
entrega el enlace + guía, nunca un dato inventado (§2.5).
"""
import requests

from ..configuracion import configuracion

URL_SOCRATA = "https://www.datos.gov.co/resource/fyc7-sbtz.json"
FUENTE = "UPRA · Frontera agrícola 1:100.000 (datos.gov.co fyc7-sbtz)"
URL_SIPRA = "https://sipra.upra.gov.co/nacional"

DEMO = {"municipio": "Mosquera", "no_condicionada_ha": 1410.9, "condicionada_ha": 11292.1}


def frontera_municipio(municipio: str) -> dict:
    """Agrega áreas por tipo_front para el municipio (SoQL)."""
    params = {
        "$select": "tipo_front,sum(area_ha) as ha",
        "$where": f"upper(municipio)='{municipio.strip().upper()}'",
        "$group": "tipo_front",
        "$limit": "10",
    }
    respuesta = requests.get(URL_SOCRATA, params=params, timeout=configuracion.sig_tiempo_fuera_seg)
    respuesta.raise_for_status()
    filas = respuesta.json()
    if not filas:
        raise ValueError(f"Sin frontera para '{municipio}' en UPRA. Verifica el nombre.")
    areas = {f.get("tipo_front"): float(f.get("ha") or 0) for f in filas}
    no_cond = round(areas.get("No condicionada", 0.0), 1)
    cond = round(areas.get("Condicionada", 0.0), 1)
    total = round(no_cond + cond, 1)
    pct = round((total and (no_cond + cond) / total * 100) or 0.0, 1)
    if cond > no_cond:
        lectura = "Mayoría condicionada: valida restricciones legales antes de sembrar (rondas, páramos, reservas)."
    else:
        lectura = "Mayoría dentro de frontera no condicionada: apto para planificar, confirma aptitud por cultivo en SIPRA."
    return {
        "municipio": municipio.strip(),
        "no_condicionada_ha": no_cond,
        "condicionada_ha": cond,
        "total_ha": total,
        "pct_en_frontera": pct,
        "lectura": lectura,
    }
