-- Contexto de lote y referencia opcional para fichas de suelo.
-- lote_id ya existe en modelos recientes; IF NOT EXISTS mantiene compatibilidad.
ALTER TABLE fichas_suelo
  ADD COLUMN IF NOT EXISTS lote_id INTEGER REFERENCES lotes(id);

-- La referencia bibliográfica es opcional en el esquema de captura.
-- La interpretación sigue exigiendo fuente; el registro crudo puede no tenerla.
ALTER TABLE fichas_suelo
  ALTER COLUMN referencia_bibliografica DROP NOT NULL;
