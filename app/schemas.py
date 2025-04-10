from typing import List, Optional, Union, Any
from pydantic import BaseModel

class PropertyValue(BaseModel):
    value: str

class PropertyCreate(BaseModel):
    uid: str
    name: str
    type: str  # 'list' or 'int'
    values: Optional[List[PropertyValue]] | int = None

class PropertyResponse(PropertyCreate):
    pass

class ProductPropertyBase(BaseModel):
    uid: str
    value: Optional[str] = None

class ProductPropertyResponse(BaseModel):
    uid: str
    name: str
    value: List | int

class ProductCreate(BaseModel):
    uid: str
    name: str
    properties: List[ProductPropertyBase]

class ProductResponse(BaseModel):
    uid: str
    name: str
    properties: List[ProductPropertyResponse]

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    count: int

class FilterResponse(BaseModel):
    count: int
    properties: dict