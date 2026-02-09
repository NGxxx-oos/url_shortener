import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from app.database import init_db
from app.models import LinkCreate, LinkResponse, LinkUpdate
from app import crud

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB
    init_db()
    yield
    # Shutdown: Clean up if needed

app = FastAPI(title="URL Shortener API", lifespan=lifespan)

@app.post("/shorten", response_model=LinkResponse, status_code=201)
async def shorten_url(payload: LinkCreate, request: Request):
    try:
        short_code = crud.create_short_link(str(payload.url), payload.custom_code)
        base_url = str(request.base_url)
        return LinkResponse(
            short_url=f"{base_url}{short_code}",
            original_url=str(payload.url),
            short_code=short_code
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/{code}")
async def redirect_to_url(code: str):
    original_url = crud.get_original_url(code)
    if original_url:
        logger.info(f"Redirecting {code} to {original_url}")
        return RedirectResponse(url=original_url)
    raise HTTPException(status_code=404, detail="Short link not found")

@app.patch("/{code}", response_model=LinkResponse)
async def update_link(code: str, payload: LinkUpdate, request: Request):
    success = crud.update_short_link(code, str(payload.url))
    if success:
        base_url = str(request.base_url)
        return LinkResponse(
            short_url=f"{base_url}{code}",
            original_url=str(payload.url),
            short_code=code
        )
    raise HTTPException(status_code=404, detail="Short link not found")

@app.delete("/{code}", status_code=204)
async def delete_link(code: str):
    success = crud.delete_short_link(code)
    if not success:
        raise HTTPException(status_code=404, detail="Short link not found")
    return None
