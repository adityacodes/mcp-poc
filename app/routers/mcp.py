from fastapi import APIRouter, Query
import loguru

router = APIRouter(tags=["MCP"])

@router.get("/greet/{name}")
def greet(name: str) -> str:
    loguru.logger.info(f"Greeting {name}")
    return f"Hello, {name}!"