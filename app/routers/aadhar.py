from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from langgraph.prebuilt import create_react_agent
import loguru
from sqlmodel import Session, select

from app.dependencies import get_session
from app.models import Aadhar

router = APIRouter(tags=["Aadhar"])

# Create
@router.post("/aadhars/", response_model=Aadhar)
def create_aadhar(aadhar: Aadhar, session: Session = Depends(get_session)):
    session.add(aadhar)
    session.commit()
    session.refresh(aadhar)
    return aadhar

# Read All
@router.get("/aadhars/", response_model=List[Aadhar])
def get_aadhars(session: Session = Depends(get_session)):
    return session.exec(select(Aadhar)).all()

# Read One
@router.get("/aadhars/{aadhar_id}", response_model=Aadhar)
def get_aadhar(aadhar_id: int, session: Session = Depends(get_session)):
    aadhar = session.get(Aadhar, aadhar_id)
    if not aadhar:
        raise HTTPException(status_code=404, detail="Aadhar not found")
    return aadhar

# Update
@router.put("/aadhars/{aadhar_id}", response_model=Aadhar)
def update_aadhar(aadhar_id: int, new_value: float, session: Session = Depends(get_session)):
    aadhar = session.get(Aadhar, aadhar_id)
    if not aadhar:
        raise HTTPException(status_code=404, detail="Aadhar not found")
    aadhar.value = new_value
    session.add(aadhar)
    session.commit()
    session.refresh(aadhar)
    return aadhar

# Delete
@router.delete("/aadhars/{aadhar_id}")
def delete_aadhar(aadhar_id: int, session: Session = Depends(get_session)):
    aadhar = session.get(Aadhar, aadhar_id)
    if not aadhar:
        raise HTTPException(status_code=404, detail="Aadhar not found")
    session.delete(aadhar)
    session.commit()
    return {"message": "Aadhar deleted"}