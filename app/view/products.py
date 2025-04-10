from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import schemas
from db.db import get_db
from service import crud

router = APIRouter()


@router.get("/{product_uid}", response_model=schemas.ProductResponse)
async def get_product(product_uid: str, db: AsyncSession = Depends(get_db)):
    product = await crud.get_product(db, product_uid)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    properties = []
    for prop in product.properties:
        prop_data = {
            "uid": prop.property_uid,
            "name": prop.property.name,
            "value": prop.property.values,
        }
        properties.append(prop_data)

    return {
        "uid": product.uid,
        "name": product.name,
        "properties": properties
    }


@router.post("/", response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate, db: AsyncSession = Depends(get_db)):
    existing_product = await crud.get_product(db, product.uid)
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this UID already exists")

    # Validate properties
    for prop in product.properties:
        property = await crud.get_property(db, prop.uid)
        if not property:
            raise HTTPException(status_code=400, detail=f"Property {prop.uid} not found")

        # if property.type == "list":
        #     if not prop.value_uid:
        #         raise HTTPException(status_code=400, detail=f"Property {prop.uid} requires value_uid")
        #
        #     # Check if value exists in property values
        #     if not any(v["uid"] == prop.value_uid for v in (property.values or [])):
        #         raise HTTPException(status_code=400, detail=f"Value {prop.value_uid} not found in property {prop.uid}")
        # else:
        #     if prop.value is None:
        #         raise HTTPException(status_code=400, detail=f"Property {prop.uid} requires numeric value")

    db_product = await crud.create_product(db, product)

    # Return the created product
    return await get_product(db_product.uid, db)


@router.delete("/{product_uid}")
async def delete_product(product_uid: str, db: AsyncSession = Depends(get_db)):
    product = await crud.delete_product(db, product_uid)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}