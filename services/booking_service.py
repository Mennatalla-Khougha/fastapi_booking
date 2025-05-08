from datetime import datetime
from re import A

from requests import get
from core.connections import db
from models.booking_model import Slot, BookingInfo, BookingStatus
from fastapi import HTTPException
import asyncio

#  TODO: Add redis to get, delete, update and set the slot

def create_booked_slot(slot: Slot) -> Slot:
    """
    Creates a booked slot with the provided booking information.

    Args:
        slot_id (str): Unique identifier for the slot.
        date (datetime): Date of the booking.
        time (datetime): Time of the booking.
        booking_info (List[BookingInfo]): List of booking information.

    Returns:
        Slot: A Slot object with the booking details.
    """
    # TODO:Add validation for date not friday and saturday
    # TODO: Add validation for time between 9 to 4:30
    # TODO: Add validation for time not in 30 minutes interval
    # TODO: Add validation for booking info fields 
    
    slot_id = str(slot.date)
    if slot.date < datetime.now():
        raise HTTPException(status_code=400, detail="Cannot book a past date")

    if not check_slot_availability(slot.date):
        raise HTTPException(status_code=409, detail="Slot already booked")

    if not slot.booking:
        raise ValueError("Booking information must be provided to book a slot.")
    
    booking_dict = slot.booking.model_dump()

    # Generate a unique slot ID based on date and time
    slot_doc = db.collection("slots").document(slot_id)
    slot_date = {
        "id": slot_id,
        "date": slot.date,
        "status": BookingStatus.booked,
        "booking": booking_dict
    }

    slot_doc.set(slot_date)

    return Slot(**slot_date)


def check_slot_availability(date: datetime) -> bool:
    """
    Check if a slot is available for booking.

    Args:
        date (datetime): Date of the booking.

    Returns:
        bool: True if the slot is available, False otherwise.
    """
    slot_id = str(date)
    slot_ref = db.collection("slots").document(slot_id).get()
    
    if slot_ref.exists:
        return False  # Slot already booked
    return True  # Slot is available


def get_slot_info(date: datetime) -> Slot:
    """
    Fetch a slot by its time.
    """
    try:
        slot_id = str(date)
        slot_ref = db.collection("slots").document(slot_id)
        slot_doc = slot_ref.get()
        
        if not slot_doc.exists:
            raise HTTPException(status_code=404, detail="Slot not found")
        
        # Convert Firestore document to a dictionary
        slot_data = slot_doc.to_dict()
        return Slot(**slot_data)
    
    except Exception as e:
        print(f"Error fetching slot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_all_booked_slots_id() -> list[str]:
    """
    Fetch all booked slots ids.
    """
    try:
        docs = await asyncio.to_thread(
            lambda: list(db.collection("slots").stream())
        )

        ids = [doc.id for doc in docs]

        return ids
    
    except Exception as e:
        print(f"Error fetching booked slots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_all_booked_slots() -> list[Slot]:
    """
    Fetch all booked slots.
    """
    try:
        ids = await get_all_booked_slots_id()

        booked_slots = []
        for slot_id in ids:
            slot_data = get_slot_info(slot_id)
            booked_slots.append(slot_data)

        return booked_slots
    
    except Exception as e:
        print(f"Error fetching booked slots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# TODO: Add a function to delete a booked slot
# TODO: Add a function to update a booked slot