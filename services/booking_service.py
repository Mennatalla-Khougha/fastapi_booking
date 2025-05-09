from datetime import datetime, time, timedelta
import json
from core.connections import db,r
from models.booking_model import Slot, BookingStatus
from fastapi import HTTPException
import asyncio



def slot_validation(slot: Slot) -> bool:
    """
    Validate the slot information.
    """
    if not slot.booking:
        raise ValueError("Booking information must be provided to book a slot.")

    now = datetime.now()
    if slot.date < now:
        raise HTTPException(status_code=400, detail="Cannot book a past date")
    slot_day = slot.date.weekday()
    if slot_day in [4, 5]:
        raise HTTPException(status_code=400, detail="Booking is not available on Friday and Saturday")
    slot_time = slot.date.time()
    start_time = time(9, 0)
    end_time = time(16, 30)
    print(f"Slot time: {slot_time}, Start time: {start_time}, End time: {end_time}")
    if not (start_time <= slot_time <= end_time):
        raise HTTPException(status_code=400, detail="Booking time must be between 9:00 AM and 4:30 PM")
    if slot_time.minute not in [0, 30]:
        raise HTTPException(status_code=400, detail="Booking time must be on the hour or half-past the hour (e.g., 9:00, 9:30)")
    if slot_time.second != 0:
        raise HTTPException(status_code=400, detail="Booking time must have 0 seconds (e.g., 9:00:00, 9:30:00)")

    return True

    # TODO: Add validation for booking info fields


def create_booked_slot(slot: Slot) -> Slot:
    """
    Creates a booked slot with the provided booking information.
    """
    slot_id = str(slot.date)
    slot_validation(slot)
    if not check_slot_availability(slot_id):
        raise HTTPException(status_code=409, detail="Slot already booked")

    booking_dict = slot.booking.model_dump()

    slot_doc = db.collection("slots").document(slot_id)
    slot_date = {
        "id": slot_id,
        "date": slot.date.isoformat(),
        "status": BookingStatus.booked,
        "booking": booking_dict
    }

    slot_doc.set(slot_date)

    slot_json = Slot(**slot_date)

    r.set(slot_id, json.dumps(slot_date), ex=60*5)

    return slot_json


def check_slot_availability(slot_id: str) -> bool:
    """
    Check if a slot is available for booking.
    """
    try:
        cached_slot = r.get(slot_id) 
        if cached_slot:
            return False
    except Exception as e:
        raise e

    slot_ref = db.collection("slots").document(slot_id).get()
    if slot_ref.exists:
        r.set(slot_id, json.dumps(slot_ref.to_dict()), ex=60)
        return False  
    
    return True 


def get_slot_info(slot_id: str) -> Slot:
    """
    Fetch a slot by its time.
    """
    try:
        cached_slot = r.get(slot_id)
        if cached_slot:
            return json.loads(cached_slot)
        slot_ref = db.collection("slots").document(slot_id)
        slot_doc = slot_ref.get()

        if not slot_doc.exists:
            raise HTTPException(status_code=404, detail="Slot not found")

        slot_data = slot_doc.to_dict()

        r.set(slot_id, json.dumps(slot_data), ex=60)
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


def delete_booked_slot(slot_id: str) -> str:
    """
    Delete a booked slot by its ID.
    """
    try:
        caches_slot = r.get(slot_id)
        if caches_slot:
            r.delete(slot_id)
        db.collection("slots").document(slot_id).delete()
        return f"Slot {slot_id} deleted successfully"
    except Exception as e:
        print(f"Error deleting booked slot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def update_booked_slot(date: datetime, slot: Slot) -> str:
    """
    Update a booked slot by its ID.
    """
    try:
        valid = slot_validation(slot)
        slot_id = str(date)
        slot_ref = db.collection("slots").document(slot_id).get()
        print(f"Slot ref: done")
        if not slot_ref.exists:
            raise HTTPException(status_code=404, detail="Slot not found")
        if not valid:
            raise HTTPException(status_code=400, detail="Invalid slot data")
        await asyncio.to_thread(
            lambda: delete_booked_slot(slot_id)
        )
        print(f"first async: done")

        await asyncio.to_thread(
            lambda: create_booked_slot(slot)
        )
        print(f"second async: done")

        slot_id = str(slot.date)

        return f"Slot {slot_id} updated successfully"
    except Exception as e:
        print(f"Error updating booked slot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def delete_all_booked_slots() -> str:
    """
    Delete all booked slots asynchronously.
    """
    try:
        ids = await get_all_booked_slots_id()

        await asyncio.gather(*[asyncio.to_thread(delete_booked_slot, id) for id in ids])

        return "All booked slots deleted successfully"
    except Exception as e:
        print(f"Error deleting all booked slots: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

async def get_available_slots(day: datetime) -> list[str]:
    """
    Fetch all available slots for a given day.
    """
    try:
        booked_slots = await get_all_booked_slots_id()
        # Generate all possible slot IDs for the given day
        start_time = time(9, 0)
        end_time = time(16, 30)
        interval_minutes = 30

        day = day.date()

        all_slots = []
        current_time = datetime.combine(day, start_time)
        end_datetime = datetime.combine(day, end_time)

        while current_time <= end_datetime:
            all_slots.append(str(current_time))
            current_time += timedelta(minutes=interval_minutes)

        available_slots = [slot for slot in all_slots if slot not in booked_slots]

        return available_slots
    except Exception as e:
        print(f"Error fetching available slots: {e}")
        raise HTTPException(status_code=500, detail=str(e))