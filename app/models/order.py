from sqlalchemy import Column, Integer, String, Float, DateTime, func, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
import datetime

from app.db.base_class import Base
from .enums import OrderStatusEnum 

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(SQLAlchemyEnum(OrderStatusEnum), default=OrderStatusEnum.PENDING, nullable=False, index=True) # Uses imported Enum

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, date='{self.order_date}', status='{self.status.value}', total={self.total_amount})>"