from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, models, schemas
from app.db.session import get_db

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
    responses={404: {"description": "Not found"}},)
@router.post(
    "/restock",
    response_model=schemas.Product,
    status_code=status.HTTP_200_OK, 
    summary="Restock a product")
def restock_product_endpoint(
    restock_data: schemas.RestockCreate,
    db: Session = Depends(get_db)):
    """
    Increase the inventory quantity for a specific product.
    """
    updated_product, error_message = crud.crud_inventory.restock_product(
        db=db, restock_info=restock_data)

    if error_message:
        status_code = status.HTTP_400_BAD_REQUEST
        if "not found" in error_message.lower():
            status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status_code,
            detail=error_message
        )

    product_with_category = crud.crud_product.get_product(db=db, product_id=updated_product.id)
    return product_with_category

@router.get(
    "/logs",
    response_model=List[schemas.InventoryLog],
    summary="Retrieve inventory change logs")
def read_inventory_logs(
    product_id: Optional[int] = Query(None, description="Filter logs by Product ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)):
    """
    Retrieve a list of inventory change logs, optionally filtered by product.
    """
    if product_id is None:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Query parameter 'product_id' is required.")

    logs = crud.crud_inventory.get_inventory_logs_for_product(
        db=db, product_id=product_id, skip=skip, limit=limit)
    return logs
