from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from backend.resources import load_resources
from backend.routes import router
from config import BASE_DIR

DIST = BASE_DIR / "web" / "dist"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_resources()
    yield


app = FastAPI(title="CardioTwin AI", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, exc: RequestValidationError):
    parts = []
    for err in exc.errors():
        loc = " → ".join(str(item) for item in err.get("loc", []) if item != "body")
        parts.append(f"{loc}: {err.get('msg', 'invalid value')}" if loc else err.get("msg", "invalid value"))
    message = "Please check the form. " + "; ".join(parts)
    return JSONResponse(status_code=422, content={"detail": message})


def _safe_file(full_path: str):
    root = DIST.resolve()
    candidate = (DIST / full_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if candidate.is_file():
        return candidate
    return None


@app.get("/", include_in_schema=False)
@app.get("/{full_path:path}", include_in_schema=False)
def spa(full_path: str = ""):
    if full_path.startswith("api/") or full_path in {"api", "docs", "redoc", "openapi.json"}:
        raise HTTPException(status_code=404, detail="Not found")
    index = DIST / "index.html"
    if not index.exists():
        raise HTTPException(status_code=503, detail="Frontend is not built yet. Run setup.bat, then start.bat.")
    if full_path:
        asset = _safe_file(full_path)
        if asset is not None:
            return FileResponse(asset)
    return FileResponse(index)
