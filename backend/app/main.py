from fastapi import FastAPI
from app.database import Base, engine
from app import models  # noqa: F401  (registra las tablas)
from app.routers import auth, horario_router, cita_router, admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MediReserva API", version="0.2.0")

app.include_router(auth.router)
app.include_router(horario_router.router)
app.include_router(cita_router.router)
app.include_router(admin_router.router)


@app.get("/")
def root():
    return {"mensaje": "MediReserva API funcionando"}