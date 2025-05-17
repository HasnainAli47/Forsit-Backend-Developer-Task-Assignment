from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from app import crud, schemas
from app.db.session import get_db
from app.models.enums import OrderStatusEnum

router = APIRouter(
    prefix="/orders",
    tags=["Orders & Sales"],
    responses={404: {"description": "Not found"}},)

@router.post(
    "/",
    response_model=schemas.Order,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order")
def create_order(
    order_in: schemas.OrderCreate,
    db: Session = Depends(get_db)):
    """
    Create a new order.
    """
    created_order, error_message = crud.crud_order.create_order(db=db, order_in=order_in)

    if not created_order:
        status_code = status.HTTP_400_BAD_REQUEST
        if "not found" in error_message.lower():
            status_code = status.HTTP_404_NOT_FOUND
        elif "insufficient stock" in error_message.lower():
             status_code = status.HTTP_409_CONFLICT

        raise HTTPException(
            status_code=status_code,
            detail=error_message
        )
    db_order_with_details = crud.crud_order.get_order(db=db, order_id=created_order.id)
    return db_order_with_details

@router.get(
    "/",
    response_model=List[schemas.Order],
    summary="Retrieve a list of orders")
def read_orders(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime.date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    status: Optional[OrderStatusEnum] = Query(None, description="Filter by order status"),
    db: Session = Depends(get_db)):
    """
    Retrieve a list of orders with various filtering options and pagination.
    """
    orders = crud.crud_order.get_orders(
        db,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        product_id=product_id,
        category_id=category_id,
        status=status)
    if orders:
        print(f"--- Inspecting first fetched order (ID: {orders[0].id}) ---")
        print(f" Order Status: {orders[0].status}")
        print(f"Accessing order.order_items: {orders[0].order_items}")
        if orders[0].order_items:
            print(f"Number of items found: {len(orders[0].order_items)}")
            print(f" First item ID: {orders[0].order_items[0].id}")
            print(f"First item quantity: {orders[0].order_items[0].quantity}")
            print(f"  First item product ID: {orders[0].order_items[0].product_id}")
        else:
            print(f"No items loaded for this order instance!")

    print("--- Returning orders from endpoint ---") 
    return orders
@router.get(
    "/{order_id}",
    response_model=schemas.Order,
    summary="Retrieve a specific order by ID"
)
def read_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve details for a specific order using its ID.
    """
    db_order = crud.crud_order.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found")
    return db_order

@router.patch(
    "/{order_id}/status",
    response_model=schemas.Order,
    summary="Update order status")
def update_order_status(
    order_id: int,
    status_update: schemas.OrderUpdate,
    db: Session = Depends(get_db)):
    """
    Update the status of an existing order (e.g., to 'completed' or 'cancelled').
    """
    if status_update.status is None:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status field is required for update."
        )

    updated_order = crud.crud_order.update_order_status(
        db=db, order_id=order_id, new_status=status_update.status)
    if updated_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    db_order_with_details = crud.crud_order.get_order(db=db, order_id=updated_order.id)
    return db_order_with_details
@router.get(
    "/stats/revenue-summary",
    response_model=List[schemas.RevenueSummary],
    summary="Get revenue summary by period")
def get_revenue_summary(
    period: str = Query("daily", description="Aggregation period: 'daily', 'weekly', 'monthly', 'annual'"),
    start_date: Optional[datetime.date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)):
    """
    Provides a summary of total revenue from completed orders,
    """
    try:
        summary = crud.crud_order.get_revenue_summary(
            db=db, period=period, start_date=start_date, end_date=end_date
        )
        return summary
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while calculating revenue.")
    