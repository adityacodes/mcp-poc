from fastapi import APIRouter

router = APIRouter(tags=["Application"])

@router.get("/")
def get_status():
    return {"status": "Application is running"}
