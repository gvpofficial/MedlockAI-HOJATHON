from fastapi import APIRouter
from app.api.v1 import auth, prescriptions, dispense, reviews, dashboard, demo

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(prescriptions.router)
api_router.include_router(dispense.router)
api_router.include_router(reviews.router)
api_router.include_router(dashboard.router)
api_router.include_router(demo.router)
