"""Autenticación JWT simple, usuario único técnico (prompt MVP)."""
import hashlib
import hmac
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

enrutador = APIRouter(prefix="/auth", tags=["auth"])
esquema_bearer = OAuth2PasswordBearer(tokenUrl="/auth/ingresar")

SECRETO = os.getenv("SECRETO_JWT", "agroapp-secreto-temporal-cambiar-en-produccion")
ALGORITMO = "HS256"
MINUTOS_EXPIRA = 480

# Usuario único técnico (MVP sin bcrypt para evitar passlib/bcrypt Windows).
# En producción mover a tabla + hash argon2.
USUARIO_TECNICO = os.getenv("USUARIO_TECNICO", "tecnico")
CLAVE_TECNICO = os.getenv("CLAVE_TECNICO", "campo123")


def _verificar(clave: str) -> bool:
    return hmac.compare_digest(
        hashlib.sha256(clave.encode()).hexdigest(),
        hashlib.sha256(CLAVE_TECNICO.encode()).hexdigest(),
    )


def crear_token(sub: str) -> str:
    expira = datetime.utcnow() + timedelta(minutes=MINUTOS_EXPIRA)
    return jwt.encode({"sub": sub, "exp": expira}, SECRETO, algorithm=ALGORITMO)


@enrutador.post("/ingresar")
def ingresar(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != USUARIO_TECNICO or not _verificar(form.password):
        raise HTTPException(401, "Credenciales inválidas")
    return {"token_acceso": crear_token(form.username), "tipo": "bearer"}


def tecnico_actual(token: str = Depends(esquema_bearer)) -> str:
    try:
        datos = jwt.decode(token, SECRETO, algorithms=[ALGORITMO])
        return str(datos.get("sub"))
    except JWTError:
        raise HTTPException(401, "Token inválido o expirado")
