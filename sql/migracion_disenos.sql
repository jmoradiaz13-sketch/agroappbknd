-- Tabla del simulador de diseño agroecológico (idempotente).
-- Ejecución: psql -d agroapp_bd -f sql/migracion_disenos.sql
CREATE TABLE IF NOT EXISTS disenos (
  id SERIAL PRIMARY KEY,
  predio_id INTEGER REFERENCES predios(id),
  unidad_nombre VARCHAR(200) NOT NULL,
  fecha DATE NOT NULL,
  version INTEGER NOT NULL,
  area_total_ha DOUBLE PRECISION,
  zona_clima VARCHAR(200),
  objetivo TEXT,
  tipo_diseno VARCHAR(50),
  nivel_transicion INTEGER,
  usos_suelo JSONB NOT NULL DEFAULT '[]',
  componentes JSONB NOT NULL DEFAULT '[]',
  rotacion_asociacion TEXT,
  referencia_bibliografica VARCHAR(300),
  creado_en TIMESTAMPTZ DEFAULT now()
);
