from pydantic import BaseModel, ConfigDict
from typing import Optional
import datetime
from app.models.enums import InventoryLogReasonEnum

class InventoryLogBase(BaseModel):
    product_id: int
    change_amount: int
    new_quantity: int
    reason: InventoryLogReasonEnum
    notes: Optional[str] = None
    order_id: Optional[int] = None
class InventoryLogCreate(InventoryLogBase):
    pass 

class InventoryLogInDBBase(InventoryLogBase):
    id: int
    timestamp: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class InventoryLog(InventoryLogInDBBase):
    pass

class RestockCreate(BaseModel):
    product_id: int
    quantity_added: int
    notes: Optional[str] = None