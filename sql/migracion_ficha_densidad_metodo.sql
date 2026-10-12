-- Ficha: densidad real + método de fósforo, Plan Maestro Etapa 3 (idempotente).
-- Ejecución: psql -d agroapp_bd -f sql/migracion_ficha_densidad_metodo.sql
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS densidad_real DOUBLE PRECISION;
ALTER TABLE fichas_suelo ADD COLUMN IF NOT EXISTS metodo_fosforo VARCHAR(20);
