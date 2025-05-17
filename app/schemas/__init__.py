# app/schemas/__init__.py
from .category import Category, CategoryCreate, CategoryUpdate
from .product import Product, ProductCreate, ProductUpdate
from .order_item import OrderItem, OrderItemCreate
from .order import Order, OrderCreate, OrderUpdate, RevenueSummary
# Add InventoryLog schemas
from .inventory_log import InventoryLog, InventoryLogCreate, RestockCreate # <--- ADD