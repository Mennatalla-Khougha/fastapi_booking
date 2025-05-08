from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class BookingStatus(str, Enum):
    booked = "booked"


class BookingInfo(BaseModel):
    name: str = Field(..., description="Name of the person making the booking", example="John Doe") 
    email: EmailStr = Field(..., description="Email of the person making the booking", example="test@gmail.com")
    company: str = Field(..., description="Company of the person making the booking", example="Google")
    country: str = Field(..., description="Country of the person making the booking", example="USA")
    whatsapp: str = Field(..., description="WhatsApp number of the person making the booking", example="+1234567890", pattern=r"^\+\d{1,3}\d{1,14}$")  
    notes: Optional[str] = Field(None, description="Notes for the booking", example="Looking forward to the meeting") 


class Slot(BaseModel):
    id: str | None = Field(None, description="Unique identifier for the slot", example="2023-10-01T14:00")
    date: datetime = Field(..., description="Date of the booking in YYYY-MM-DD format", example="2023-10-01T00:00")
    # time: datetime = Field(..., description="Time of the booking in HH:MM format", example="14:00")
    status: BookingStatus = Field(default=BookingStatus.booked, description="Status of the booking")
    booking: BookingInfo = Field(None, description="List of bookings for the slot")
