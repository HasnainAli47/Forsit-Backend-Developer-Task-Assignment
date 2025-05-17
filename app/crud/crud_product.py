from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app import crud
from app.models.enums import InventoryLogReasonEnum
from app.models.product import Product as ProductModel
from app.models.category import Category as CategoryModel 
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.config import settings

def _add_low_stock_flag(product: ProductModel):
    """Adds the is_low_stock attribute to a product model instance."""
    if product:
        product.is_low_stock = product.quantity < settings.LOW_STOCK_THRESHOLD
    return product
def get_product(db: Session, product_id: int) -> Optional[ProductModel]:
    """
    Retrieves a single product by its ID, eagerly loading the category,
    and adds the is_low_stock flag.
    """
    product = db.query(ProductModel).options(
        joinedload(ProductModel.category)
    ).filter(ProductModel.id == product_id).first()

    return _add_low_stock_flag(product) 

def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    low_stock: Optional[bool] = None 
) -> List[ProductModel]:
    """
    Retrieves a list of products with pagination and optional filters,
    eagerly loading categories, and adds the is_low_stock flag to each.
    Can filter by low_stock status.
    """
    query = db.query(ProductModel).options(joinedload(ProductModel.category))

    if category_id is not None:
        query = query.filter(ProductModel.category_id == category_id)

    if low_stock is True:
        query = query.filter(ProductModel.quantity < settings.LOW_STOCK_THRESHOLD)
    elif low_stock is False:
        query = query.filter(ProductModel.quantity >= settings.LOW_STOCK_THRESHOLD)

    products = query.order_by(ProductModel.name).offset(skip).limit(limit).all() 

    return [_add_low_stock_flag(p) for p in products]


def create_product(db: Session, product: ProductCreate) -> ProductModel:
    """
    Creates a new product in the database.
    Checks if the provided category_id exists first.
    """
    db_category = db.query(CategoryModel).filter(CategoryModel.id == product.category_id).first()
    if not db_category:
        return None

    db_product = ProductModel(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity,
        category_id=product.category_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
def update_product(db: Session, db_product: ProductModel, product_in: ProductUpdate) -> Optional[ProductModel]:
    """
    Updates an existing product. Logs inventory change if quantity is updated.
    """
    update_data = product_in.model_dump(exclude_unset=True)

    if not update_data:
        return db_product

    if "category_id" in update_data:
        new_category_id = update_data["category_id"]
        db_category = db.query(CategoryModel).filter(CategoryModel.id == new_category_id).first()
        if not db_category:
            return None 

    original_quantity = db_product.quantity
    quantity_changed = False
    new_quantity_value = None
    if "quantity" in update_data:
        new_quantity_value = update_data["quantity"]
        if new_quantity_value != original_quantity:
            quantity_changed = True
            if new_quantity_value < 0:
                 print(f"Attempted to set negative quantity for product {db_product.id}")
                 return None 

    for field, value in update_data.items():
        setattr(db_product, field, value)

    try:
        db.add(db_product) 

        if quantity_changed:
            change = new_quantity_value - original_quantity
            crud.crud_inventory.create_inventory_log(
                db=db,
                product_id=db_product.id,
                change_amount=change,
                reason=InventoryLogReasonEnum.MANUAL_UPDATE,
                notes=f"Updated via API PATCH /products/{db_product.id}" 
            )

        db.commit()
        db.refresh(db_product)
        updated_product_with_flag = get_product(db=db, product_id=db_product.id)
        return updated_product_with_flag

    except Exception as e:
        db.rollback()
        print(f"Error updating product {db_product.id}: {e}")
        return None
def delete_product(db: Session, product_id: int) -> Optional[ProductModel]:
    """
    Deletes a product by its ID.
    Returns the deleted product object or None if not found.
    """
    db_product = get_product(db=db, product_id=product_id) 
    if db_product:
        db.delete(db_product)
        db.commit()
        return db_product
    return None 
