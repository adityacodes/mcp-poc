from langchain.tools import tool
from sqlmodel import Session, select
from app.models import Aadhar
from app.dependencies import get_session  # Ensure this gives a working session

@tool
def validate_aadhar_number(value: str) -> str:
    """
    Validates an Aadhaar number and checks if it exists in the database.
    """
    if len(value) != 12 or not value.isdigit():
        return "Invalid Aadhaar: Must be a 12-digit number."
    if value[0] in ['0', '1']:
        return "Invalid Aadhaar: Cannot start with 0 or 1."

    # DB lookup
    with next(get_session()) as session:
        result = session.exec(select(Aadhar).where(Aadhar.value == value)).first()
        if result:
            return f"Valid Aadhaar number. Found in database with ID: {result.id}."
        else:
            return "Valid Aadhaar number. Not found in database."
