import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class CustomBase(Base):
    __abstract__ = True
    __table_args__ = {'schema': 'product_management'}


class Product(CustomBase):
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("product_management.categories.category_id"), nullable=False)
    manufacturer = Column(String, nullable=False)

    # Связь с Category
    category = relationship("Category", back_populates="products", lazy='joined')

    # Связь с ProductAttributeValues
    attribute_values = relationship("ProductAttributeValues", back_populates="product", lazy="selectin")

    # Связь с ProductImage
    images = relationship("ProductImage", back_populates="product", lazy='selectin')

    # Связь с Review
    reviews = relationship("Review", back_populates="product", lazy="selectin")


class Category(CustomBase):
    __tablename__ = "categories"

    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)

    # Связь с Product
    products = relationship("Product", back_populates="category")

    # Связь с CategoryAttributes
    category_attributes = relationship("CategoryAttributes")


class Attribute(CustomBase):
    __tablename__ = "attributes"

    attribute_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    category_attributes = relationship("CategoryAttributes")
    product_attribute_values = relationship("ProductAttributeValues", back_populates="attribute")


class CategoryAttributes(CustomBase):
    __tablename__ = "category_attributes"

    category_attribute_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_management.categories.category_id", ondelete="CASCADE"),
        primary_key=True)

    attribute_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_management.attributes.attribute_id", ondelete="CASCADE"),
        primary_key=True)

    # Связь с Category
    category = relationship("Category", back_populates="category_attributes", lazy='joined')

    # Связь с Attribute
    attribute = relationship("Attribute", back_populates="category_attributes", lazy='joined')


class ProductAttributeValues(CustomBase):
    __tablename__ = "product_attribute_values"

    product_attribute_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_management.products.product_id", ondelete="CASCADE"),
        primary_key=True)

    attribute_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_management.attributes.attribute_id", ondelete="CASCADE"),
        primary_key=True)

    value = Column(Text, nullable=False)

    # Связь с Product
    product = relationship("Product", back_populates="attribute_values")

    # Связь с Attribute
    attribute = relationship("Attribute", back_populates="product_attribute_values")


class ProductImage(CustomBase):
    __tablename__ = "product_images"

    image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("product_management.products.product_id", ondelete="CASCADE"))
    image_name = Column(String, nullable=False)
    description = Column(Text)

    # Связь с Product
    product = relationship("Product", back_populates="images", lazy='joined')


class Review(CustomBase):
    __tablename__ = "reviews"

    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("product_management.products.product_id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), nullable=False)
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)

    # Связь с Product
    product = relationship("Product", back_populates="reviews")
