from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

from tables import Base


class Property(Base):
    __tablename__ = "properties"

    uid = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    values = Column(JSON, nullable=True)


class Product(Base):
    __tablename__ = "products"

    uid = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)

    properties = relationship("ProductProperty", back_populates="product")


class ProductProperty(Base):
    __tablename__ = "product_properties"

    id = Column(Integer, primary_key=True, index=True)
    product_uid = Column(String, ForeignKey("products.uid"))
    property_uid = Column(String, ForeignKey("properties.uid"))

    product = relationship("Product", back_populates="properties")
    property = relationship("Property")