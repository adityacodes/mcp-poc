from fastapi import APIRouter

router = APIRouter(tags=["Extraction"])

@router.get("/aditya")
def get_status():
    return {"status": "Application is running"}
