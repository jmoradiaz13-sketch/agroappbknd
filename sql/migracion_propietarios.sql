-- Propietarios del predio, Plan Maestro Etapa 1 (idempotente).
-- Ejecución: psql -d agroapp_bd -f sql/migracion_propietarios.sql
CREATE TABLE IF NOT EXISTS propietarios (
  id SERIAL PRIMARY KEY,
  predio_id INTEGER NOT NULL UNIQUE REFERENCES predios(id),
  nombre_completo VARCHAR(200) NOT NULL,
  cedula VARCHAR(50),
  contacto VARCHAR(200),
  tenencia VARCHAR(50),
  vocacion VARCHAR(100),
  mano_obra_familiar INTEGER,
  fecha_actualizacion TIMESTAMPTZ DEFAULT now()
);
