from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
import datetime
from .order_item import OrderItem, OrderItemCreate
from app.models.enums import OrderStatusEnum

class OrderCreate(BaseModel):
    status: OrderStatusEnum = OrderStatusEnum.PENDING 
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None 

class OrderBase(BaseModel):
    id: int
    order_date: datetime.datetime
    total_amount: float
    status: OrderStatusEnum
    model_config = ConfigDict(from_attributes=True)

class Order(OrderBase):
    items: List[OrderItem] = Field(..., alias="order_items")

class RevenueSummary(BaseModel):
    period: str
    total_revenue: float