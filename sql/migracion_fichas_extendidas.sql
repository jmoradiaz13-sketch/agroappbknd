-- Migración idempotente: columnas del plan "Determina las características de tu suelo".
-- Ejecución: psql -d agroapp_bd -f sql/migracion_fichas_extendidas.sql
-- En bases nuevas creadas desde el modelo SQLAlchemy no hace falta.
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS tipo_evaluacion VARCHAR(20);
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS clima_reciente TEXT;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS textura_tacto VARCHAR(100);
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS compactacion VARCHAR(100);
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS infiltracion VARCHAR(100);
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS porosidad_pct DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS capacidad_campo_pct DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS pmp_pct DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS ph_campo DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS ce_campo_ds_m DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS carbonatos VARCHAR(100);
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS sintomas_visuales TEXT;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS aluminio_cmol_kg DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS saturacion_al_pct DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS azufre_mg_kg DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS nodulacion VARCHAR(100);
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS olor_suelo VARCHAR(100);
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS descomposicion_mo VARCHAR(100);
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS carbono_biomasa_microbiana DOUBLE PRECISION;
