from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import routes
from .core.graph import graph_manager
from .db.session import SessionLocal

app = FastAPI(
    title="Path Finding API",
    description="API for finding the shortest path on a road network.",
    version="0.1.0"
)

# --- CORS Middleware Configuration ---
# This allows the frontend (running on a different origin) to communicate with the backend.
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)
# -------------------------------------

@app.on_event("startup")
def on_startup():
    """Load the graph into memory when the application starts."""
    db = SessionLocal()
    try:
        graph_manager.load_graph(db)
    finally:
        db.close()

# Include the API router
app.include_router(routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Path Finding API"}
