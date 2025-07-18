

# Define the model
from typing import Optional
from sqlmodel import Field, SQLModel


class Aadhar(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    value: str