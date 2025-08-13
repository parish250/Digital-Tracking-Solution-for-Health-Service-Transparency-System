from fastapi import FastAPI
from app.db_config import Base, engine
from app.routes import (
    auth_routes,
    warehouse_routes,
    shipment_routes,
    feedback_routes,
    distribution_center_routes,
    food_aid_item_routes
)

# Create FastAPI app
app = FastAPI(title="Digital Tracking Solution for Health Service Transparency")

# Create all tables at startup
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(warehouse_routes.router, prefix="/warehouses", tags=["Warehouses"])
app.include_router(shipment_routes.router, prefix="/shipments", tags=["Shipments"])
app.include_router(feedback_routes.router, prefix="/feedbacks", tags=["Feedbacks"])
app.include_router(distribution_center_routes.router, prefix="/distribution_centers", tags=["Distribution Centers"])
app.include_router(food_aid_item_routes.router, prefix="/food_aid_items", tags=["Food Aid Items"])
