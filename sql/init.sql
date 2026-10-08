-- Habilita PostGIS y verifica MAGNA-SIRGAS (EPSG:4686) según AGENTS.md
CREATE EXTENSION IF NOT EXISTS postgis;
-- EPSG:4686 viene en spatial_ref_sys de PostGIS; verificamos:
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM spatial_ref_sys WHERE srid = 4686) THEN
    RAISE NOTICE 'SRID 4686 no encontrado, revisar instalación PostGIS';
  END IF;
END $$;
