from sqlmodel import SQLModel, Session, create_engine, select
from app.database.models import ExtractedData
from app.dependencies import engine

def insert_data(aadhar: str, mobile: str):
    with Session(engine) as session:
        stmt = select(ExtractedData).where(
            ExtractedData.aadhar == aadhar,
            ExtractedData.mobile == mobile
        )
        if not session.exec(stmt).first():
            session.add(ExtractedData(aadhar=aadhar, mobile=mobile))
        session.commit()

def validate_aadhar_mobile(aadhar: str, mobile: str) -> dict:
    with Session(engine) as session:
        # Check Aadhar existence
        aadhar_stmt = select(ExtractedData).where(ExtractedData.aadhar == aadhar)
        aadhar_result = session.exec(aadhar_stmt).first()
        aadhar_exists = aadhar_result is not None

        # Check Mobile existence
        mobile_stmt = select(ExtractedData).where(ExtractedData.mobile == mobile)
        mobile_result = session.exec(mobile_stmt).first()
        mobile_exists = mobile_result is not None

        print("Aadhar exists:", aadhar_exists, "| Mobile exists:", mobile_exists)

        return {
            "aadhar_exists": aadhar_exists,
            "mobile_exists": mobile_exists
        }