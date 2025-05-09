from datetime import datetime
from fastapi import APIRouter, HTTPException
from models.booking_model import Slot
from services.booking_service import check_slot_availability, create_booked_slot, delete_all_booked_slots, get_all_booked_slots, \
    get_all_booked_slots_id, get_slot_info, delete_booked_slot, update_booked_slot

router = APIRouter()

    
@router.get("/slot", response_model=Slot)
def get_slots(slot_id: str):
    """
    Endpoint to get all slot info.
    """
    try:
        # Fetch all slots from the database
        return get_slot_info(slot_id)
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/book_slot", response_model=Slot)
async def book_slot(slot:Slot):
    """
    Endpoint to book a slot with the provided booking information.
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
async def check_slot_availability_endpoint(slot_id: str):
    """
    Endpoint to check if a slot is available for booking.
    """
    try:
        return check_slot_availability(slot_id)
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


@router.delete("/delete_slot", response_model=str)
async def delete_booked_slot_endpoint(slot_id: str):
    """
    Endpoint to delete a booked slot.
    """
    try:
        return delete_booked_slot(slot_id)

    except HTTPException as e:
        raise e

@router.put("/update_slot", response_model=str)
async def update_booked_slot_endpoint(date: datetime, slot: Slot):
    """
    Update a booked slot by its ID.
    """
    try:
        return await update_booked_slot(date, slot)
    except HTTPException as e:
        raise e


@router.delete("/delete_all_slots", response_model=str)
async def delete_all_booked_slots_endpoint():
    """
    Endpoint to delete all booked slots.
    """
    try:
        return await delete_all_booked_slots()
    except HTTPException as e:
        raise e