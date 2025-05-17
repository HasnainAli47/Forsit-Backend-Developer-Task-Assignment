from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.routers import categories, products, orders, inventory

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce Admin API",
    description="API for managing e-commerce sales, inventory, and products.",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the E-commerce Admin API"}

app.include_router(categories.router)
app.include_router(products.router) 
app.include_router(orders.router)
app.include_router(inventory.router)
