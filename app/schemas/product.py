from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
import datetime
from .category import Category

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int = 0

class ProductCreate(ProductBase):
    category_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    category_id: Optional[int] = None

class ProductInDBBase(ProductBase):
    id: int
    category_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    category: Category

    model_config = ConfigDict(from_attributes=True)

class Product(ProductInDBBase):
    is_low_stock: bool = Field(..., description="True if product quantity is below the configured threshold")

class ProductInDB(ProductInDBBase):
    pass