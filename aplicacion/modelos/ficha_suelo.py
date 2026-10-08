"""Ficha de suelo INMUTABLE: serie temporal, nunca UPDATE, siempre INSERT nueva versión.

Fuente: .agents/rules/AGENTS.md §3. Trazabilidad bibliográfica obligatoria a src/*.pdf
Unidades almacenamiento: cmol/kg, mg/kg, %, dS/m.
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, DateTime, func
from .predio import Predio  # noqa: F401  (asegura registro de tablas)
from .lote import Lote  # noqa: F401
from ..base_datos import Base


class FichaSuelo(Base):
    __tablename__ = "fichas_suelo"

    id = Column(Integer, primary_key=True)
    predio_id = Column(Integer, ForeignKey("predios.id"), nullable=False)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    fecha = Column(Date, nullable=False)
    version = Column(Integer, nullable=False)  # 1,2,3... por predio
    tipo = Column(String(20), nullable=False, default="laboratorio")  # laboratorio|campo|mixto
    tipo_evaluacion = Column(String(20), nullable=True)  # campo|laboratorio|mixta
    clima_reciente = Column(Text, nullable=True)
    profundidad_cm = Column(Float, nullable=True)
    laboratorio_observador = Column(String(200), nullable=True)
    metodo_campo = Column(String(20), nullable=True)  # VSA|DRES|PGPE|ninguno
    indice_calidad = Column(Float, nullable=True)

    calcio_cmol_kg = Column(Float, nullable=True)
    magnesio_cmol_kg = Column(Float, nullable=True)
    potasio_cmol_kg = Column(Float, nullable=True)
    sodio_cmol_kg = Column(Float, nullable=True)
    aluminio_cmol_kg = Column(Float, nullable=True)
    saturacion_al_pct = Column(Float, nullable=True)
    fosforo_mg_kg = Column(Float, nullable=True)
    azufre_mg_kg = Column(Float, nullable=True)
    materia_organica_pct = Column(Float, nullable=True)
    nitrogeno_pct = Column(Float, nullable=True)
    conductividad_ds_m = Column(Float, nullable=True)
    # Químico extendido MVP
    ph_agua = Column(Float, nullable=True)
    ph_kcl = Column(Float, nullable=True)
    sodio_cmol_kg = Column(Float, nullable=True)
    cic_cmol_kg = Column(Float, nullable=True)
    hierro_mg_kg = Column(Float, nullable=True)
    manganeso_mg_kg = Column(Float, nullable=True)
    zinc_mg_kg = Column(Float, nullable=True)
    cobre_mg_kg = Column(Float, nullable=True)
    boro_mg_kg = Column(Float, nullable=True)
    # Físico MVP + extendido plan fichas (campo y laboratorio)
    textura_tacto = Column(String(100), nullable=True)
    arena_pct = Column(Float, nullable=True)
    limo_pct = Column(Float, nullable=True)
    arcilla_pct = Column(Float, nullable=True)
    estructura = Column(String(100), nullable=True)
    densidad_aparente = Column(Float, nullable=True)
    porosidad_pct = Column(Float, nullable=True)
    capacidad_campo_pct = Column(Float, nullable=True)
    pmp_pct = Column(Float, nullable=True)
    compactacion = Column(String(100), nullable=True)
    infiltracion = Column(String(100), nullable=True)
    color_munsell = Column(String(50), nullable=True)
    pedregosidad = Column(String(100), nullable=True)
    profundidad_efectiva_cm = Column(Float, nullable=True)
    # Químico campo
    ph_campo = Column(Float, nullable=True)
    ce_campo_ds_m = Column(Float, nullable=True)
    carbonatos = Column(String(100), nullable=True)
    sintomas_visuales = Column(Text, nullable=True)
    # Biológico MVP + extendido
    lombrices_conteo = Column(Integer, nullable=True)
    nodulacion = Column(String(100), nullable=True)
    olor_suelo = Column(String(100), nullable=True)
    descomposicion_mo = Column(String(100), nullable=True)
    macrofauna = Column(Text, nullable=True)
    respiracion_suelo = Column(Float, nullable=True)
    carbono_biomasa_microbiana = Column(Float, nullable=True)
    micorrizas = Column(String(100), nullable=True)
    cobertura_vegetal_pct = Column(Float, nullable=True)

    referencia_bibliografica = Column(String(300), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
