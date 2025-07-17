from fastapi import APIRouter
from . import (mcp)

api_router = APIRouter(prefix="/api")

api_router.include_router(mcp.router)
