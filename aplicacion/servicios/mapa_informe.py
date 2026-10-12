"""Mapa SVG para el informe PDF: lotes + puntos sin dependencias externas.

Proyección lineal del bbox WGS84 a 640×400. Honesto: croquis de ubicación
con norte y escala aproximada, no cartografía oficial.
"""
from __future__ import annotations

ANCHO, ALTO, MARGEN = 640, 400, 30


def _bbox(geometrias: list[dict]) -> tuple[float, float, float, float] | None:
    xs, ys = [], []
    for g in geometrias:
        tipo = g.get("type")
        coords = g.get("coordinates", [])
        if tipo == "Polygon":
            for anillo in coords:
                for x, y in anillo:
                    xs.append(x)
                    ys.append(y)
        elif tipo == "Point":
            xs.append(coords[0])
            ys.append(coords[1])
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def croquis_svg(
    lotes: list[dict],
    puntos: list[dict],
    titulo: str = "Croquis del predio (WGS84)",
) -> str:
    """lotes: [{nombre, geojson}], puntos: [{codigo, lat, lng}]."""
    geometrias = [l["geojson"] for l in lotes]
    geometrias += [{"type": "Point", "coordinates": [p["lng"], p["lat"]]} for p in puntos]
    caja = _bbox(geometrias)
    if caja is None:
        return "<p>Sin geometrías para el croquis: dibuja lotes y puntos en /lote y /sig.</p>"
    lon_min, lat_min, lon_max, lat_max = caja
    dx = (lon_max - lon_min) or 0.001
    dy = (lat_max - lat_min) or 0.001

    def px(lon: float, lat: float) -> tuple[float, float]:
        x = MARGEN + (lon - lon_min) / dx * (ANCHO - 2 * MARGEN)
        y = MARGEN + (1 - (lat - lat_min) / dy) * (ALTO - 2 * MARGEN)
        return (round(x, 1), round(y, 1))

    elementos = []
    for l in lotes:
        anillos = l["geojson"].get("coordinates", [])
        if not anillos:
            continue
        pts = " ".join(f"{x},{y}" for x, y in (px(lon, lat) for lon, lat in anillos[0]))
        elementos.append(
            f'<polygon points="{pts}" fill="#10b981" fill-opacity="0.25" '
            f'stroke="#059669" stroke-width="2"><title>{l["nombre"]}</title></polygon>'
        )
        cx, cy = px(sum(p[0] for p in anillos[0]) / len(anillos[0]), sum(p[1] for p in anillos[0]) / len(anillos[0]))
        elementos.append(f'<text x="{cx}" y="{cy}" font-size="13" text-anchor="middle" fill="#0f172a">{l["nombre"]}</text>')
    for p in puntos:
        x, y = px(p["lng"], p["lat"])
        elementos.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#dc2626"><title>{p["codigo"]}</title></circle>')
        elementos.append(f'<text x="{x + 8}" y="{y + 4}" font-size="11" fill="#0f172a">{p["codigo"]}</text>')

    escala_m = round(dx * 111320 * (1 if dy >= dx else dx / dy))
    return f"""<svg viewBox="0 0 {ANCHO} {ALTO}" width="100%" role="img" aria-label="{titulo}">
<rect x="0" y="0" width="{ANCHO}" height="{ALTO}" fill="#f1f5f9"/>
<text x="{ANCHO - MARGEN}" y="{MARGEN - 8}" font-size="14" text-anchor="end">N ↑</text>
{''.join(elementos)}
<text x="{MARGEN}" y="{ALTO - 8}" font-size="11" fill="#475569">Ancho aprox. {escala_m} m · Croquis WGS84, no oficial</text>
<text x="{MARGEN}" y="{MARGEN - 8}" font-size="11" fill="#475569">■ Lote  ● Punto de muestreo</text>
</svg>"""
