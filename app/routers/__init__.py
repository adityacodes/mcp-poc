from fastapi import APIRouter
from . import (mcp, aditya)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(mcp.router)
api_router.include_router(aditya.router)
