"""Esquemas Pydantic en español con validación de unidades."""
from datetime import date
from pydantic import BaseModel, Field


class FichaSueloCrear(BaseModel):
    predio_identificador: str = Field(min_length=1)
    # Lote/parcela opcional dentro del predio.
    lote_nombre: str | None = Field(default=None, max_length=200)
    fecha: date
    tipo_evaluacion: str | None = Field(default=None, pattern='^(campo|laboratorio|mixta)$')
    clima_reciente: str | None = Field(default=None, max_length=500)
    profundidad_cm: float | None = Field(default=None, ge=0, le=200)
    laboratorio_observador: str | None = Field(default=None, max_length=200)
    # Sitio de muestreo (Datos del terreno)
    latitud: float | None = Field(default=None, ge=-90, le=90)
    longitud: float | None = Field(default=None, ge=-180, le=180)
    precision_m: float | None = Field(default=None, ge=0, le=10000)
    msnm: float | None = Field(default=None, ge=-500, le=6000)
    pendiente_sitio_pct: float | None = Field(default=None, ge=0, le=200)
    posicion_relieve: str | None = Field(default=None, pattern='^(cima|hombro|ladera|pie|valle)$')
    uso_actual: str | None = Field(default=None, max_length=200)
    solicitante: str | None = Field(default=None, max_length=200)
    tenencia_sitio: str | None = Field(default=None, pattern='^(propietario|arrendatario|poseedor|otro)$')
    manejo_reciente: str | None = Field(default=None, max_length=1000)
    vereda: str | None = Field(default=None, max_length=100)
    municipio: str | None = Field(default=None, max_length=100)
    departamento: str | None = Field(default=None, max_length=100)
    # Físicas
    textura_tacto: str | None = Field(default=None, max_length=100)
    compactacion: str | None = Field(default=None, max_length=100)
    infiltracion: str | None = Field(default=None, max_length=100)
    estructura: str | None = Field(default=None, max_length=100)
    estructura_vess: int | None = Field(default=None, ge=1, le=5)
    densidad_aparente: float | None = Field(default=None, ge=0, le=3)
    densidad_real: float | None = Field(default=None, ge=0, le=3)
    porosidad_pct: float | None = Field(default=None, ge=0, le=100)
    capacidad_campo_pct: float | None = Field(default=None, ge=0, le=100)
    pmp_pct: float | None = Field(default=None, ge=0, le=100)
    color_munsell: str | None = Field(default=None, max_length=50)
    munsell_h: str | None = Field(default=None, max_length=10)
    munsell_v: float | None = Field(default=None, ge=0, le=10)
    munsell_c: float | None = Field(default=None, ge=0, le=10)
    color_estado: str | None = Field(default=None, max_length=20)
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
    metodo_fosforo: str | None = Field(default=None, pattern='^(Bray II|Olsen|otro)$')
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
    referencia_bibliografica: str | None = Field(
        default=None,
        max_length=300,
        description="Fuente registrada (opcional, se cuadra después)"
    )


class FichaSueloRespuesta(FichaSueloCrear):
    id: int
    version: int
