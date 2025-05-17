from sqlalchemy.orm import Session
from typing import List, Optional, Tuple 

from app.models.inventory_log import InventoryLog as InventoryLogModel
from app.models.enums import InventoryLogReasonEnum
from app.models.product import Product as ProductModel
from app.schemas.inventory_log import RestockCreate
def create_inventory_log(
    db: Session,
    product_id: int,
    change_amount: int,
    reason: InventoryLogReasonEnum,
    order_id: Optional[int] = None,
    notes: Optional[str] = None
) -> InventoryLogModel:
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise ValueError(f"Product with ID {product_id} not found for logging.")
    current_quantity = product.quantity
    new_quantity_after_change = current_quantity + change_amount
    db_log = InventoryLogModel(
        product_id=product_id,
        change_amount=change_amount,
        new_quantity=new_quantity_after_change,
        reason=reason,
        order_id=order_id,
        notes=notes
    )
    db.add(db_log)
    db.flush()
    return db_log
def get_inventory_logs_for_product(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[InventoryLogModel]:
    return (
        db.query(InventoryLogModel)
        .filter(InventoryLogModel.product_id == product_id)
        .order_by(InventoryLogModel.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
def restock_product(db: Session, restock_info: RestockCreate) -> Tuple[Optional[ProductModel], Optional[InventoryLogModel], str]:
    """
    Increases the quantity of a product and logs the restock event.
    """
    if restock_info.quantity_added <= 0:
        return None, None, "Quantity added must be positive."

    try:
        product = db.query(ProductModel).filter(ProductModel.id == restock_info.product_id).with_for_update().first()

        if not product:
            db.rollback()
            return None, None, f"Product with ID {restock_info.product_id} not found."

        product.quantity += restock_info.quantity_added

        log_entry = create_inventory_log(
            db=db,
            product_id=product.id,
            change_amount=restock_info.quantity_added, #
            reason=InventoryLogReasonEnum.RESTOCK,
            notes=restock_info.notes
        )

        db.commit()

        db.refresh(product)
        db.refresh(log_entry)

        return product, log_entry, "" 

    except Exception as e:
        db.rollback()
        print(f"Error restocking product {restock_info.product_id}: {e}") 
        return None, None, f"An unexpected error occurred during restock: {e}"