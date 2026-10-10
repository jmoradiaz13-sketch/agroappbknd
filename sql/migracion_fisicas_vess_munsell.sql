-- Módulo físico VESS + Munsell estructurado (idempotente).
-- Ejecución: psql -d agroapp_bd -f sql/migracion_fisicas_vess_munsell.sql
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS estructura_vess INTEGER;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS munsell_h VARCHAR(10);
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS munsell_v DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS munsell_c DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS color_estado VARCHAR(20);
