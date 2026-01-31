from app.routers.zones import router as zones_router
from app.routers.devices import router as devices_router
from app.routers.sensors import router as sensors_router
from app.routers.predictions import router as predictions_router
from app.routers.websocket import router as websocket_router

__all__ = [
    "zones_router",
    "devices_router",
    "sensors_router",
    "predictions_router",
    "websocket_router",
]
