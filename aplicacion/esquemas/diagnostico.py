"""Esquemas de diagnóstico y estrategia (español)."""
from pydantic import BaseModel, Field


class Hallazgo(BaseModel):
    parametro: str
    unidad: str
    valor: float
    estado: str  # deficiente|optimo|exceso
    porque: str
    referencia_bibliografica: str


class DiagnosticoRespuesta(BaseModel):
    predio_identificador: str
    ficha_version: int
    hallazgos: list[Hallazgo]


class EstrategiaCrear(BaseModel):
    ficha_id: int
    descripcion: str = Field(min_length=5)
    decision_tecnico: str = Field(pattern="^(aceptada|rechazada|editada)$")
    referencia_bibliografica: str = Field(min_length=3)
