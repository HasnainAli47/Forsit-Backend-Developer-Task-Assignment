from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Enum as SQLAlchemyEnum


from app.db.base_class import Base
from .enums import InventoryLogReasonEnum

class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    change_amount = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    reason = Column(SQLAlchemyEnum(InventoryLogReasonEnum), nullable=False, index=True)
    notes = Column(String(255), nullable=True)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)

    def __repr__(self):
        return f"<InventoryLog(id={self.id}, product_id={self.product_id}, change={self.change_amount}, new_qty={self.new_quantity}, reason='{self.reason.value}')>"