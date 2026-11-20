from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from app import models
from app.database import engine
from app.routers import admin, animais, auth, meus, procedimentos, tutores
from app.security import limiter




def rate_limit(request, exc):
        return JSONResponse(status_code=429, content="Too many requests.")


app = FastAPI(title="Vetsys API", description="API para gerenciamento de tutores e pets", version="2.2.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
   )

from app.routers import tutores, animais, procedimentos, meus, admin, auth
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(tutores.router)
app.include_router(animais.router)
app.include_router(procedimentos.router)
app.include_router(meus.router)

