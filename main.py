from typing import Collection
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.connections import db, r
from google.cloud import firestore
from routers import booking_router

app = FastAPI()

app.include_router(booking_router.router, prefix="/booking", tags=["booking"])

import os
app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "static")), name="static")


@app.get("/")
def read_root():
    return {"message": "FastAPI + Firestore + Redis is running!"}

@app.get("/firestore")
async def read_firestore():
    # test Firestore connection
    doc = db.collection('test').document('connection_check')
    doc.set({"status": "connected", "timestamp": firestore.SERVER_TIMESTAMP})
    return {"firestore_status": doc.get().to_dict()}

@app.get("/redis")
async def read_redis():
    # test Redis connection
    r.set('connection_check', 'connected')
    return {"redis_status": r.get('connection_check')}