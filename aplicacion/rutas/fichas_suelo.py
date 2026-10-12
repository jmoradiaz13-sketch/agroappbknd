"""Rutas de fichas: solo crea nuevas versiones, jamás actualiza ni borra."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..base_datos import obtener_sesion
from ..modelos.predio import Predio
from ..modelos.ficha_suelo import FichaSuelo
from ..esquemas.ficha import FichaSueloCrear

enrutador = APIRouter(prefix="/fichas-suelo", tags=["fichas-suelo"])


@enrutador.post("/nueva-version")
def crear_nueva_version(datos: FichaSueloCrear, sesion: Session = Depends(obtener_sesion)):
    predio = sesion.query(Predio).filter_by(identificador=datos.predio_identificador).first()
    if not predio:
        raise HTTPException(404, f"Predio {datos.predio_identificador} no encontrado")
    max_version = sesion.query(func.max(FichaSuelo.version)).filter_by(predio_id=predio.id).scalar() or 0
    ficha = FichaSuelo(
        predio_id=predio.id,
        fecha=datos.fecha,
        version=max_version + 1,
        tipo_evaluacion=datos.tipo_evaluacion,
        clima_reciente=datos.clima_reciente,
        profundidad_cm=datos.profundidad_cm,
        laboratorio_observador=datos.laboratorio_observador,
        textura_tacto=datos.textura_tacto,
        compactacion=datos.compactacion,
        infiltracion=datos.infiltracion,
        estructura=datos.estructura,
        estructura_vess=datos.estructura_vess,
        densidad_aparente=datos.densidad_aparente,
        densidad_real=datos.densidad_real,
        porosidad_pct=datos.porosidad_pct,
        capacidad_campo_pct=datos.capacidad_campo_pct,
        pmp_pct=datos.pmp_pct,
        color_munsell=datos.color_munsell,
        munsell_h=datos.munsell_h,
        munsell_v=datos.munsell_v,
        munsell_c=datos.munsell_c,
        color_estado=datos.color_estado,
        profundidad_efectiva_cm=datos.profundidad_efectiva_cm,
        ph_campo=datos.ph_campo,
        ce_campo_ds_m=datos.ce_campo_ds_m,
        carbonatos=datos.carbonatos,
        sintomas_visuales=datos.sintomas_visuales,
        ph_agua=datos.ph_agua,
        ph_kcl=datos.ph_kcl,
        calcio_cmol_kg=datos.calcio_cmol_kg,
        magnesio_cmol_kg=datos.magnesio_cmol_kg,
        potasio_cmol_kg=datos.potasio_cmol_kg,
        sodio_cmol_kg=datos.sodio_cmol_kg,
        aluminio_cmol_kg=datos.aluminio_cmol_kg,
        saturacion_al_pct=datos.saturacion_al_pct,
        cic_cmol_kg=datos.cic_cmol_kg,
        fosforo_mg_kg=datos.fosforo_mg_kg,
        metodo_fosforo=datos.metodo_fosforo,
        azufre_mg_kg=datos.azufre_mg_kg,
        materia_organica_pct=datos.materia_organica_pct,
        nitrogeno_pct=datos.nitrogeno_pct,
        conductividad_ds_m=datos.conductividad_ds_m,
        hierro_mg_kg=datos.hierro_mg_kg,
        manganeso_mg_kg=datos.manganeso_mg_kg,
        zinc_mg_kg=datos.zinc_mg_kg,
        cobre_mg_kg=datos.cobre_mg_kg,
        boro_mg_kg=datos.boro_mg_kg,
        arena_pct=datos.arena_pct,
        limo_pct=datos.limo_pct,
        arcilla_pct=datos.arcilla_pct,
        lombrices_conteo=datos.lombrices_conteo,
        nodulacion=datos.nodulacion,
        olor_suelo=datos.olor_suelo,
        descomposicion_mo=datos.descomposicion_mo,
        respiracion_suelo=datos.respiracion_suelo,
        carbono_biomasa_microbiana=datos.carbono_biomasa_microbiana,
        micorrizas=datos.micorrizas,
        cobertura_vegetal_pct=datos.cobertura_vegetal_pct,
        referencia_bibliografica=datos.referencia_bibliografica,
    )
    sesion.add(ficha)
    sesion.commit()
    sesion.refresh(ficha)
    return {"id": ficha.id, "version": ficha.version, "porque": f"Sugerencia trazada a {ficha.referencia_bibliografica}"}
