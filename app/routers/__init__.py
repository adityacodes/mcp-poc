from fastapi import APIRouter
from . import (mcp, aadhar)

api_router = APIRouter(prefix="/api")

api_router.include_router(mcp.router)
api_router.include_router(aadhar.router)
