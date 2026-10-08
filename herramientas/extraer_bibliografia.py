"""Extrae texto y tablas de src/*.pdf a datos_bibliograficos/*.json + references.json.

Uso: python herramientas/extraer_bibliografia.py [--limite-paginas N]
Regla: no inventa; si falta dato -> pendiente_de_validacion.
"""
import argparse
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ.parent / "src"
SALIDA = RAIZ / "datos_bibliograficos"

CATEGORIAS = {
    "soil_field_methods": ["visual", "vsa", "dres", "field_assessment", "evaluacion_visual", "muestreo"],
    "soil_lab_interpretation": ["guia_para_la_evaluacion_de_la_calidad", "buenas_practicas", "descripcion_y_muestreo", "zonas_homogeneas", "precision", "oxisol", "caatinga"],
    "agroforestry": ["agroforesteria", "agroforestry", "agroecologia", "saf_cacao", "cacao"],
    "gis_sources": ["modelo_de_sistema_gestion", "determinacion_de_zonas"],
}


def categorizar(nombre: str) -> str:
    n = nombre.lower()
    for categoria, claves in CATEGORIAS.items():
        if any(c in n for c in claves):
            return categoria
    return "soil_lab_interpretation"


def extraer_pdf(ruta: Path, limite_paginas: int = 0) -> dict:
    try:
        import pdfplumber
    except ImportError:
        pdfplumber = None
    try:
        from pypdf import PdfReader
    except ImportError:
        PdfReader = None

    paginas_texto: list[str] = []
    tablas: list[list[list[str | None]]] = []
    num_paginas = 0

    if pdfplumber is not None:
        try:
            with pdfplumber.open(str(ruta)) as pdf:
                total = len(pdf.pages)
                num_paginas = total
                objetivo = pdf.pages[:limite_paginas] if limite_paginas else pdf.pages
                for i, pagina in enumerate(objetivo):
                    texto = pagina.extract_text() or ""
                    paginas_texto.append(texto[:8000])
                    try:
                        for t in (pagina.extract_tables() or [])[:3]:
                            tablas.append([[(str(c)[:200] if c else None) for c in fila[:8]] for fila in t[:20]])
                    except Exception:
                        pass
        except Exception as e:
            paginas_texto.append(f"[ERROR pdfplumber: {e}]")

    if not paginas_texto and PdfReader is not None:
        try:
            lector = PdfReader(str(ruta))
            num_paginas = len(lector.pages)
            objetivo = lector.pages[:limite_paginas] if limite_paginas else lector.pages
            for p in objetivo:
                paginas_texto.append((p.extract_text() or "")[:8000])
        except Exception as e:
            paginas_texto.append(f"[ERROR pypdf: {e}]")

    texto_total = "\n".join(paginas_texto)
    # Heurística simple: buscar menciones de parámetros para uso_en_proyecto
    parametros = ["materia organica", "fosforo", "potasio", "calcio", "magnesio", "ph", "conductividad",
                  "nitrogeno", "textura", "vsa", "dres", "rusle", "ndvi", "agroforester"]
    hallados = sorted({p for p in parametros if p in texto_total.lower()})
    return {
        "archivo": ruta.name,
        "paginas": num_paginas,
        "paginas_extraidas": len(paginas_texto),
        "texto_muestra": paginas_texto[:3],
        "num_tablas": len(tablas),
        "tablas_muestra": tablas[:2],
        "parametros_mencionados": hallados or ["pendiente_de_validacion"],
        "estado": "extraido" if texto_total.strip() else "pendiente_de_validacion",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite-paginas", type=int, default=5, help="0 = todas")
    args = ap.parse_args()

    pdfs = sorted(SRC.glob("*.pdf"))
    print(f"PDFs encontrados: {len(pdfs)}")
    SALIDA.mkdir(exist_ok=True)
    for cat in list(CATEGORIAS) + ["soil_lab_interpretation"]:
        (SALIDA / cat).mkdir(exist_ok=True)

    referencias = []
    for pdf in pdfs:
        print(f"- {pdf.name} ...", flush=True)
        datos = extraer_pdf(pdf, args.limite_paginas)
        categoria = categorizar(pdf.name)
        destino = SALIDA / categoria / (pdf.stem + ".json")
        destino.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
        referencias.append({
            "id": pdf.stem,
            "tipo": "manual" if "guia" in pdf.name or "manual" in pdf.name else "articulo",
            "autores": "pendiente_de_validacion",
            "año": "pendiente_de_validacion",
            "titulo": pdf.stem.replace("_", " "),
            "fuente": f"src/{pdf.name}",
            "doi": "pendiente_de_validacion",
            "categoria": categoria,
            "datos_extraidos": {"parametros": datos["parametros_mencionados"], "tablas": datos["num_tablas"]},
            "uso_en_proyecto": "interpretacion_suelos" if "soil" in categoria else categoria,
            "estado": datos["estado"],
        })
    (SALIDA / "references.json").write_text(json.dumps(referencias, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(referencias)} referencias -> {SALIDA / 'references.json'}")


if __name__ == "__main__":
    main()
