from fastapi import APIRouter
from . import (mcp)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(mcp.router)
