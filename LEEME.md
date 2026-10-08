# AgroApp Backend (FastAPI + PostGIS EPSG:4686)

## Ejecutar (requiere Python 3.11 + Docker)

```powershell
docker compose up -d db  # desde la raíz
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn aplicacion.principal:app --reload  # http://localhost:8000/docs
```

Reglas: fichas inmutables (solo POST /fichas-suelo/nueva-version), unidades fijas,
todo en español, geometrías en MAGNA-SIRGAS.
