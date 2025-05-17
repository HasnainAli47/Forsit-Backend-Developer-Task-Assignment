import enum

class OrderStatusEnum(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class InventoryLogReasonEnum(str, enum.Enum):
    SALE = "sale" 
    RESTOCK = "restock"             
    MANUAL_UPDATE = "manual_update" 
    RETURN = "return"               
    INITIAL_STOCK = "initial_stock" 
    ADJUSTMENT = "adjustment"      