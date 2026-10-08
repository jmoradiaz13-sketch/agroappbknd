"""App FastAPI principal."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .configuracion import configuracion
from .rutas import predios, fichas_suelo, analisis, diagnostico, informes, lotes, auth, referencias_monitoreo

app = FastAPI(title="AgroForestapp API", description="Gestión de fincas y suelos MAGNA-SIRGAS EPSG:4686", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", configuracion.url_frontal],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predios.enrutador)
app.include_router(fichas_suelo.enrutador)
app.include_router(analisis.enrutador)
app.include_router(diagnostico.enrutador)
app.include_router(informes.enrutador)
app.include_router(lotes.enrutador)
app.include_router(auth.enrutador)
app.include_router(referencias_monitoreo.enrutador_ref)
app.include_router(referencias_monitoreo.enrutador_mon)


@app.get("/")
def raiz():
    return {"mensaje": "AgroForestapp API lista", "docs": "/docs", "idioma": "es-CO"}
