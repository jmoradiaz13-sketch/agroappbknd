"""Motor SQLAlchemy 2.0 + sesión."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .configuracion import configuracion


class Base(DeclarativeBase):
    pass


motor = create_engine(configuracion.url_base_datos, future=True)
FabricaSesiones = sessionmaker(bind=motor, autoflush=False, autocommit=False)


def obtener_sesion():
    sesion = FabricaSesiones()
    try:
        yield sesion
    finally:
        sesion.close()
