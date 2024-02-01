import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float, DateTime
from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class CustomBase(Base):
    __abstract__ = True
    __table_args__ = {'schema': 'shopping_cart'}


class Cart(CustomBase):
    __tablename__ = 'cart'

    cart_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, onupdate=datetime.utcnow)

    # Relationship with CartItem
    items = relationship("CartItem", back_populates="cart")


class CartItem(CustomBase):
    __tablename__ = 'cart_item'

    cart_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey('shopping_cart.cart.cart_id', ondelete='CASCADE'))
    product_id = Column(UUID(as_uuid=True), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)

    # Relationship with Cart
    cart = relationship("Cart", back_populates="items")


class Orders(CustomBase):
    __tablename__ = 'orders'

    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    shipping_address = Column(String, nullable=False)

    # Relationship with OrderDetails
    details = relationship("OrderDetails", back_populates="order")


class OrderDetails(CustomBase):
    __tablename__ = 'order_details'

    order_details_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('shopping_cart.orders.order_id', ondelete='CASCADE'))
    product_id = Column(UUID(as_uuid=True), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    # Relationship with Orders
    order = relationship("Orders", back_populates="details")
