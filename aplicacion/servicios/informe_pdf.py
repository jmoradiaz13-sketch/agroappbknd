"""Generación de informe PDF (WeasyPrint en Docker, fallback HTML local).

AGENTS.md: WeasyPrint para PDF. En Windows local WeasyPrint exige GTK;
por eso la importación es perezosa: en dev sin GTK se devuelve HTML,
en Docker (ver Dockerfile con libcairo/pango) se devuelve PDF real.
Todo en español, con porqué + referencia bibliográfica.
"""

from ..servicios.motor_diagnostico import diagnosticar


def construir_html_informe(
    predio_identificador: str,
    ficha_version: int,
    valores: dict,
    hallazgos: list[dict],
    mapa_svg: str = "",
) -> str:
    filas = "\n".join(
        f"<tr><td>{h['parametro']}</td><td>{h['valor']} {h['unidad']}</td>"
        f"<td>{h['estado']}</td><td>{h['porque']}</td><td>{h['referencia_bibliografica'] or '—'}</td></tr>"
        for h in hallazgos
    )
    return f"""<!doctype html><html lang="es-CO"><head><meta charset="utf-8">
<title>Informe AgroForestapp {predio_identificador} v{ficha_version}</title>
<style>body{{font-family:sans-serif;margin:32px}}table{{border-collapse:collapse;width:100%}}
td,th{{border:1px solid #555;padding:8px}}h1{{color:#2f6b2f}}</style></head><body>
<h1>AgroForestapp — Informe de finca {predio_identificador} (ficha v{ficha_version})</h1>
<p>El técnico decide: este informe sugiere, el técnico acepta/rechaza/edita en campo.</p>
<h2>Croquis del predio</h2>
{mapa_svg}
<table><thead><tr><th>Parámetro</th><th>Valor</th><th>Estado</th><th>Por qué</th><th>Fuente</th></tr></thead>
<tbody>{filas}</tbody></table>
<p>Valores sin dato presente se omiten (no se inventan). Unidades: cmol/kg, mg/kg, %, dS/m.</p>
</body></html>"""


def generar_pdf_bytes(html: str) -> bytes | None:
    """Retorna PDF si WeasyPrint+GTK disponible, si no None (usar HTML)."""
    try:
        from weasyprint import HTML  # import perezoso
        return HTML(string=html).write_pdf()
    except Exception:
        return None


def informe_para_ficha(
    predio_identificador: str,
    ficha_version: int,
    valores: dict,
    mapa_svg: str = "",
) -> tuple[str, bytes | None]:
    hallazgos = diagnosticar(valores)
    html = construir_html_informe(predio_identificador, ficha_version, valores, hallazgos, mapa_svg)
    return html, generar_pdf_bytes(html)
