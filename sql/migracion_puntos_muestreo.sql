-- Puntos de muestreo GPS (idempotente).
-- Ejecución: psql -d agroapp_bd -f sql/migracion_puntos_muestreo.sql
CREATE TABLE IF NOT EXISTS puntos_muestreo (
  id SERIAL PRIMARY KEY,
  predio_identificador VARCHAR(50) NOT NULL,
  lote_nombre VARCHAR(200),
  codigo VARCHAR(50) NOT NULL UNIQUE,
  lat DOUBLE PRECISION NOT NULL,
  lng DOUBLE PRECISION NOT NULL,
  fecha DATE,
  creado_en TIMESTAMPTZ DEFAULT now()
);
