from pydantic import BaseModel, ConfigDict
from typing import Optional
from .product import Product as ProductSchema

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price_per_unit: Optional[float] = None
class OrderItemBase(OrderItemCreate):
    id: int
    order_id: int
    price_per_unit: float
    model_config = ConfigDict(from_attributes=True)
class OrderItem(OrderItemBase):
    product: ProductSchema