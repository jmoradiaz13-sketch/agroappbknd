-- Fotos de muestra offline (idempotente).
-- Ejecución: psql -d agroapp_bd -f sql/migracion_fotos.sql
CREATE TABLE IF NOT EXISTS fotos_muestra (
  id SERIAL PRIMARY KEY,
  ficha_id INTEGER REFERENCES fichas_suelo(id),
  predio_identificador VARCHAR(100) NOT NULL,
  lote_nombre VARCHAR(200),
  tipo VARCHAR(20) NOT NULL DEFAULT 'muestra',
  imagen BYTEA NOT NULL,
  miniatura BYTEA,
  lat DOUBLE PRECISION,
  lng DOUBLE PRECISION,
  cobertura_pct DOUBLE PRECISION,
  fecha DATE NOT NULL,
  observaciones TEXT,
  creado_en TIMESTAMPTZ DEFAULT now()
);
