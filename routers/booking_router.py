from datetime import date, datetime
from fastapi import APIRouter, HTTPException
from models.booking_model import Slot, BookingInfo, BookingStatus
from services.booking_service import  check_slot_availability, create_booked_slot, get_all_booked_slots, get_all_booked_slots_id, get_slot_info

router = APIRouter()

    
@router.get("/slot", response_model=Slot)
async def get_slots(date: datetime):
    """
    Endpoint to get all available slots.
    """
    try:
        # Fetch all slots from the database
        return get_slot_info(date)
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/book_slot", response_model=Slot)
async def book_slot(slot:Slot):
    """
    Endpoint to book a slot with the provided booking information.

    Args:
        slot_id (str): Unique identifier for the slot.
        date (datetime): Date of the booking.
        time (datetime): Time of the booking.
        booking_info (List[BookingInfo]): List of booking information.

    Returns:
        Slot: A Slot object with the booking details.
    """
    try:
        if not slot.booking:
            raise ValueError("Booking information must be provided to book a slot.")
    
        booked_slot = create_booked_slot(slot)
        return booked_slot
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise e
    

@router.get("/check_slot", response_model=bool)
async def check_slot_availability_endpoint(date: datetime):
    """
    Endpoint to check if a slot is available for booking.

    Args:
        date (datetime): Date of the booking.

    Returns:
        bool: True if the slot is available, False otherwise.
    """
    try:
        return check_slot_availability(date)
    except Exception as e:
        raise e
    

@router.get("/ids", response_model=list[str])
async def get_all_booked_slots_id_endpoint():
    try:
        return await get_all_booked_slots_id()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/", response_model=list[Slot])
async def get_all_booked_slots_endpoint():
    """
    Endpoint to get all booked slots.
    """
    try:
        return await get_all_booked_slots()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# TODO: Add a endpoint to delete a booked slot
# TODO: Add a endpoint to update a booked slot