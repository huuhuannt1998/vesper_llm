
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import tasks, sim, devices

app = FastAPI(title="VESPER Backend (LLM Integrated)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(sim.router, prefix="/sim", tags=["sim"])

@app.get("/")
def root():
    return {"ok": True, "service": "vesper-backend-llm"}
