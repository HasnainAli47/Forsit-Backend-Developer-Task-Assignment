from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select
from typing import List, Optional, Dict, Any, Tuple 
import datetime
from decimal import Decimal
import traceback 
from app import crud 

from app.models.order import Order as OrderModel
from app.models.enums import OrderStatusEnum, InventoryLogReasonEnum
from app.models.order_item import OrderItem as OrderItemModel
from app.models.product import Product as ProductModel
from app.schemas.order import OrderCreate
from .crud_product import _add_low_stock_flag

def create_order(db: Session, order_in: OrderCreate) -> Tuple[Optional[OrderModel], str]:
    """
    Creates a new order, associated order items, updates product quantities,
    and logs inventory changes within a single database transaction.
    """
    if not order_in.items:
        return None, "Order must contain at least one item."

    print("\n--- Starting create_order ---") 
    try:
        total_amount = Decimal("0.0")
        order_items_instances: List[OrderItemModel] = []
        products_to_update: Dict[int, ProductModel] = {} 
        log_creation_data = [] 

        print("1. Validating items and locking products...")
        for item_in in order_in.items:
            print(f"  Processing item for product ID: {item_in.product_id}")
            product = db.query(ProductModel).filter(ProductModel.id == item_in.product_id).with_for_update().first()
            if not product:
                print(f"  ERROR: Product ID {item_in.product_id} not found.")
                db.rollback()
                return None, f"Product with ID {item_in.product_id} not found."

            if product.quantity < item_in.quantity:
                print(f"  ERROR: Insufficient stock for product ID {item_in.product_id}. Available: {product.quantity}, Required: {item_in.quantity}.")
                db.rollback()
                return None, f"Insufficient stock for product ID {item_in.product_id}. Available: {product.quantity}, Required: {item_in.quantity}."

            if product.id not in products_to_update:
                 products_to_update[product.id] = product

            price = Decimal(str(item_in.price_per_unit)) if item_in.price_per_unit is not None else Decimal(str(product.price))
            item_total = price * Decimal(item_in.quantity)
            total_amount += item_total
            print(f"  Item Total: {item_total}, Running Order Total: {total_amount}")

            order_item_instance = OrderItemModel(
                product_id=item_in.product_id,
                quantity=item_in.quantity,
                price_per_unit=float(price)
            )
            order_items_instances.append(order_item_instance)

            log_creation_data.append({
                "product_id": item_in.product_id,
                "change_amount": -item_in.quantity, 
                "reason": InventoryLogReasonEnum.SALE
            })
        print("Item validation complete.")

        print("2. Creating Order object...")
        db_order = OrderModel(
            total_amount=float(total_amount),
            status=order_in.status,
        )
        db.add(db_order)
        print("Order object added to session.")

        print("3. Linking items, updating quantities...")
        for item_model in order_items_instances:
            product_to_update = products_to_update[item_model.product_id]

            item_model.order = db_order 

            product_to_update.quantity += (-item_model.quantity) 
            if product_to_update.quantity < 0:
                 print(f"  ERROR: Stock became negative for product {product_to_update.id} during update.")
                 db.rollback()
                 raise ValueError(f"Stock became negative for product {product_to_update.id}. Aborting.")

            db.add(item_model)
            db.add(product_to_update)
        print("Items linked, quantities updated in session.")


        print("4. Flushing session to get Order ID...")
        db.flush()
        print(f"Order ID after flush: {db_order.id}")

        if not db_order.id:
             print("  ERROR: Failed to obtain Order ID after flush.")
             db.rollback()
             raise ValueError("Failed to obtain Order ID after flush.")

        print(f"5. Creating {len(log_creation_data)} inventory log entries...")
        for log_data in log_creation_data:
            crud.crud_inventory.create_inventory_log(
                db=db,
                product_id=log_data["product_id"],
                change_amount=log_data["change_amount"],
                reason=log_data["reason"],
                order_id=db_order.id # Use the flushed Order ID
            )
        print("Inventory log entries prepared.")

        print("6. Committing transaction...")
        db.commit()
        print("Transaction committed.")

        print(f"--- Finished create_order Successfully for Order ID: {db_order.id} ---")
        return db_order, ""

    except Exception as e:
        print("\n--- Rolling back transaction due to error in create_order ---")
        db.rollback()
        print(f"Error details: {e}")
        traceback.print_exc() 
        print("-------------------------------------------------------------")
        return None, f"An unexpected error occurred during order creation: {e}"
def get_order(db: Session, order_id: int) -> Optional[OrderModel]:
    """
    Retrieves a single order by ID, eagerly loading items and their products.
    """
    order = (
        db.query(OrderModel)
        .options(
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.product).joinedload(ProductModel.category)
        )
        .filter(OrderModel.id == order_id)
        .first()
    )

    # --- ADD THIS BLOCK ---
    if order and order.order_items:
        for item in order.order_items:
            if item.product: # Check if product loaded
                _add_low_stock_flag(item.product)
    # --- END BLOCK ---

    return order


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    status: Optional[OrderStatusEnum] = None
) -> List[OrderModel]:
    """
    Retrieves a list of orders with filtering and pagination.
    Eagerly loads items and their products.
    """
    query = db.query(OrderModel).options(
         joinedload(OrderModel.order_items).joinedload(OrderItemModel.product).joinedload(ProductModel.category)
    )

    if start_date:
        query = query.filter(OrderModel.order_date >= start_date)
    if end_date:
        query = query.filter(OrderModel.order_date < (end_date + datetime.timedelta(days=1)))
    if status:
        query = query.filter(OrderModel.status == status)

    needs_join = product_id is not None or category_id is not None
    if needs_join:
        query = query.distinct() 

    orders = query.order_by(OrderModel.order_date.desc()).offset(skip).limit(limit).all()

    for order in orders:
        if order.order_items:
            for item in order.order_items:
                if item.product:
                    _add_low_stock_flag(item.product)

    return orders

def update_order_status(db: Session, order_id: int, new_status: OrderStatusEnum) -> Optional[OrderModel]:
    """ Updates the status of an order. """
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order:
        db_order.status = new_status
        db.commit()
        db.refresh(db_order)
        return db_order
    return None
def delete_order(db: Session, order_id: int) -> Optional[OrderModel]:
    """ Deletes an order. Associated items are deleted via cascade. """
    db_order = get_order(db, order_id) 
    if db_order:
        db.delete(db_order)
        db.commit()
        return db_order
    return None


def get_revenue_summary(
    db: Session,
    period: str, 
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
) -> List[Dict[str, Any]]:
    """ Calculates total revenue grouped by the specified period (SQLite compatible). """
    period_format_map = {
        "daily": "%Y-%m-%d",
        "weekly": "%Y-%W",  
        "monthly": "%Y-%m",
        "annual": "%Y",
    }
    strftime_format = period_format_map.get(period.lower())
    if not strftime_format:
        raise ValueError("Invalid period specified. Use 'daily', 'weekly', 'monthly', or 'annual'.")

    query = select(
        func.strftime(strftime_format, OrderModel.order_date).label("period_label"),
        func.sum(OrderModel.total_amount).label("total_revenue")
    ).group_by("period_label").order_by("period_label")

    query = query.where(OrderModel.status == OrderStatusEnum.COMPLETED)
    if start_date:
        query = query.where(OrderModel.order_date >= start_date)
    if end_date:
        query = query.where(OrderModel.order_date < (end_date + datetime.timedelta(days=1)))

    results = db.execute(query).mappings().all() 

    formatted_results = []
    for row in results:
        formatted_results.append({
            "period": row["period_label"], 
            "total_revenue": row["total_revenue"]
        })

    return formatted_results
