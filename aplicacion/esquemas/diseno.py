"""Esquemas del simulador de diseño agroecológico (referencia opcional)."""
from datetime import date
from pydantic import BaseModel, Field


class UsoSuelo(BaseModel):
    uso: str = Field(min_length=1, max_length=100)
    porcentaje: float = Field(ge=0, le=100)


class ComponenteDiseno(BaseModel):
    rol: str = Field(min_length=1, max_length=100)
    especie: str = Field(default="", max_length=200)
    detalle: str | None = Field(default=None, max_length=500)


class DisenoCrear(BaseModel):
    predio_identificador: str | None = Field(default=None, description="Opcional: si se simula desde cero va nulo")
    unidad_nombre: str = Field(min_length=1, max_length=200)
    fecha: date
    area_total_ha: float | None = Field(default=None, ge=0, le=100000)
    zona_clima: str | None = Field(default=None, max_length=200)
    objetivo: str | None = Field(default=None, max_length=2000)
    tipo_diseno: str | None = Field(default=None, max_length=50)
    nivel_transicion: int | None = Field(default=None, ge=1, le=4)
    usos_suelo: list[UsoSuelo] = Field(default_factory=list)
    componentes: list[ComponenteDiseno] = Field(default_factory=list)
    rotacion_asociacion: str | None = Field(default=None, max_length=2000)
    referencia_bibliografica: str | None = Field(default=None, max_length=300)


class DisenoRespuesta(DisenoCrear):
    id: int
    version: int
