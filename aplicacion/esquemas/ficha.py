"""Esquemas Pydantic en español con validación de unidades."""
from datetime import date
from pydantic import BaseModel, Field


class FichaSueloCrear(BaseModel):
    predio_identificador: str = Field(min_length=1)
    fecha: date
    tipo_evaluacion: str | None = Field(default=None, pattern='^(campo|laboratorio|mixta)$')
    clima_reciente: str | None = Field(default=None, max_length=500)
    profundidad_cm: float | None = Field(default=None, ge=0, le=200)
    laboratorio_observador: str | None = Field(default=None, max_length=200)
    # Físicas
    textura_tacto: str | None = Field(default=None, max_length=100)
    compactacion: str | None = Field(default=None, max_length=100)
    infiltracion: str | None = Field(default=None, max_length=100)
    estructura: str | None = Field(default=None, max_length=100)
    densidad_aparente: float | None = Field(default=None, ge=0, le=3)
    porosidad_pct: float | None = Field(default=None, ge=0, le=100)
    capacidad_campo_pct: float | None = Field(default=None, ge=0, le=100)
    pmp_pct: float | None = Field(default=None, ge=0, le=100)
    color_munsell: str | None = Field(default=None, max_length=50)
    profundidad_efectiva_cm: float | None = Field(default=None, ge=0, le=300)
    # Químicas campo
    ph_campo: float | None = Field(default=None, ge=0, le=14)
    ce_campo_ds_m: float | None = Field(default=None, ge=0, le=20)
    carbonatos: str | None = Field(default=None, max_length=100)
    sintomas_visuales: str | None = Field(default=None, max_length=1000)
    # Químicas laboratorio
    ph_agua: float | None = Field(default=None, ge=0, le=14)
    ph_kcl: float | None = Field(default=None, ge=0, le=14)
    calcio_cmol_kg: float | None = Field(default=None, ge=0, le=30)
    magnesio_cmol_kg: float | None = Field(default=None, ge=0, le=15)
    potasio_cmol_kg: float | None = Field(default=None, ge=0, le=5)
    sodio_cmol_kg: float | None = Field(default=None, ge=0, le=10)
    aluminio_cmol_kg: float | None = Field(default=None, ge=0, le=10)
    saturacion_al_pct: float | None = Field(default=None, ge=0, le=100)
    cic_cmol_kg: float | None = Field(default=None, ge=0, le=60)
    fosforo_mg_kg: float | None = Field(default=None, ge=0, le=500)
    azufre_mg_kg: float | None = Field(default=None, ge=0, le=2000)
    materia_organica_pct: float | None = Field(default=None, ge=0, le=20)
    nitrogeno_pct: float | None = Field(default=None, ge=0, le=2)
    conductividad_ds_m: float | None = Field(default=None, ge=0, le=20)
    hierro_mg_kg: float | None = Field(default=None, ge=0, le=2000)
    manganeso_mg_kg: float | None = Field(default=None, ge=0, le=2000)
    zinc_mg_kg: float | None = Field(default=None, ge=0, le=2000)
    cobre_mg_kg: float | None = Field(default=None, ge=0, le=2000)
    boro_mg_kg: float | None = Field(default=None, ge=0, le=2000)
    arena_pct: float | None = Field(default=None, ge=0, le=100)
    limo_pct: float | None = Field(default=None, ge=0, le=100)
    arcilla_pct: float | None = Field(default=None, ge=0, le=100)
    # Biológicas
    lombrices_conteo: int | None = Field(default=None, ge=0, le=10000)
    nodulacion: str | None = Field(default=None, max_length=100)
    olor_suelo: str | None = Field(default=None, max_length=100)
    descomposicion_mo: str | None = Field(default=None, max_length=100)
    respiracion_suelo: float | None = Field(default=None, ge=0, le=10000)
    carbono_biomasa_microbiana: float | None = Field(default=None, ge=0, le=10000)
    micorrizas: str | None = Field(default=None, max_length=100)
    cobertura_vegetal_pct: float | None = Field(default=None, ge=0, le=100)
    referencia_bibliografica: str = Field(
        min_length=3,
        description="Fuente en src/, ej: guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.12"
    )


class FichaSueloRespuesta(FichaSueloCrear):
    id: int
    version: int
