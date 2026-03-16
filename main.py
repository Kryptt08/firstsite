from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db, seed_db
from routers import pets, admin, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialise and seed the database
    init_db()
    seed_db()
    yield


app = FastAPI(
    title="BGS.GG API",
    description="Backend for OG Bubble Gum Simulator Value List",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock this down to your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates (for the admin panel UI)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routers
app.include_router(pets.router,    prefix="/api/pets",    tags=["Pets"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(admin.router,   prefix="/admin",       tags=["Admin"])


@app.get("/")
async def root():
    return {"message": "BGS.GG API is running", "docs": "/docs"}
