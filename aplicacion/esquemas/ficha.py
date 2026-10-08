"""Esquemas Pydantic en español con validación de unidades."""
from datetime import date
from pydantic import BaseModel, Field


class FichaSueloCrear(BaseModel):
    predio_identificador: str = Field(min_length=1)
    fecha: date
    profundidad_cm: float | None = Field(default=None, ge=0, le=200)
    laboratorio_observador: str | None = Field(default=None, max_length=200)
    ph_agua: float | None = Field(default=None, ge=0, le=14)
    ph_kcl: float | None = Field(default=None, ge=0, le=14)
    calcio_cmol_kg: float | None = Field(default=None, ge=0, le=30)
    magnesio_cmol_kg: float | None = Field(default=None, ge=0, le=15)
    potasio_cmol_kg: float | None = Field(default=None, ge=0, le=5)
    sodio_cmol_kg: float | None = Field(default=None, ge=0, le=10)
    cic_cmol_kg: float | None = Field(default=None, ge=0, le=60)
    fosforo_mg_kg: float | None = Field(default=None, ge=0, le=500)
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
    referencia_bibliografica: str = Field(
        min_length=3,
        description="Fuente en src/, ej: guia_para_la_evaluacion_de_la_calidad_y_salud_del_suelo.pdf p.12"
    )


class FichaSueloRespuesta(FichaSueloCrear):
    id: int
    version: int
