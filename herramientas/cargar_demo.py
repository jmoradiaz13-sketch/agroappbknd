"""Carga demo Andina (Tibacuy) en PostGIS. Requiere DB arriba; si no, imprime JSON demo.

Uso: python herramientas/cargar_demo.py [--solo-json]
"""
import argparse
import json
from datetime import date

DEMO = {
    "predio": {"identificador": "finca-mirador", "nombre": "Finca El Mirador",
               "propietario": "Familia Demo", "municipio": "Tibacuy", "departamento": "Cundinamarca"},
    "lotes": [{"nombre": "Lote Café", "uso_actual": "café con sombrío"},
              {"nombre": "Lote Potrero", "uso_actual": "potrero"}],
    "fichas": 2, "estrategias": 1, "monitoreos": 1,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-json", action="store_true")
    args = ap.parse_args()
    if args.solo_json:
        print(json.dumps(DEMO, ensure_ascii=False, indent=2))
        return
    try:
        from aplicacion.base_datos import FabricaSesiones
        from aplicacion.modelos.predio import Predio
        from aplicacion.modelos.lote import Lote
        from aplicacion.modelos.ficha_suelo import FichaSuelo
        sesion = FabricaSesiones()
        if sesion.query(Predio).filter_by(identificador="finca-mirador").first():
            print("Demo ya existe en DB")
            return
        # Geometrías mínimas 4686 (punto buffer para demo sin shape real)
        from sqlalchemy import func
        predio = Predio(identificador="finca-mirador", nombre="Finca El Mirador",
                        propietario="Familia Demo", municipio="Tibacuy", departamento="Cundinamarca")
        sesion.add(predio)
        sesion.flush()
        sesion.execute(Predio.__table__.update().where(Predio.id == predio.id).values(
            geometria=func.ST_GeomFromText("POLYGON((-74.46 4.33,-74.44 4.33,-74.44 4.35,-74.46 4.35,-74.46 4.33))", 4686)))
        lote = Lote(predio_id=predio.id, nombre="Lote Café", uso_actual="café con sombrío")
        sesion.add(lote)
        sesion.flush()
        sesion.execute(Lote.__table__.update().where(Lote.id == lote.id).values(
            geometria=func.ST_GeomFromText("POLYGON((-74.458 4.34,-74.448 4.34,-74.448 4.348,-74.458 4.348,-74.458 4.34))", 4686)))
        sesion.add(FichaSuelo(predio_id=predio.id, lote_id=lote.id, fecha=date.today(), version=1,
                              materia_organica_pct=3.4, fosforo_mg_kg=18, potasio_cmol_kg=0.35,
                              calcio_cmol_kg=4.5, magnesio_cmol_kg=1.2, conductividad_ds_m=0.6,
                              nitrogeno_pct=0.18, tipo="mixto",
                              referencia_bibliografica="guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.12-18"))
        sesion.commit()
        print("Demo cargada en PostGIS: finca-mirador + Lote Café + ficha v1")
    except Exception as e:
        print(f"Sin DB ({e}). JSON demo:")
        print(json.dumps(DEMO, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
