import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_mcp import FastApiMCP
from loguru import logger
from app.dependencies import CORS, init_db
from app.services import init_defaults
from app.routers import api_router
from dotenv import load_dotenv
load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent
UPLOAD_FOLDER = f"{BASE_DIR}/generated/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()
    init_defaults()
    logger.info("Default Initialization completed")

CORS(app)

@app.get("/", include_in_schema=False)
async def redirect():
    return RedirectResponse(url="/docs")

app.include_router(api_router)

app.mount("/api/v1/files", StaticFiles(directory=UPLOAD_FOLDER), name="files")

mcp = FastApiMCP(app, include_operations=["validate_aadhar", "get_aadhars"])
mcp.mount()
