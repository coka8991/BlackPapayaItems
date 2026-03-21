from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers.items import router as items_router
from core.logger_config import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Black Papaya Items")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://blackpapayaitems.onrender.com"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(items_router)

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend" / "dist"

    
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    """Serve the React SPA. Static assets first, then fallback to index.html."""
    file = FRONTEND_DIR / full_path
    if file.is_file():
        return FileResponse(file)
    return FileResponse(FRONTEND_DIR / "index.html")
