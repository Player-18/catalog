from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import schemas
from db.db import get_db
from service import crud

router = APIRouter()


@router.post("/", response_model=schemas.PropertyResponse)
async def create_property(property: schemas.PropertyCreate, db: AsyncSession = Depends(get_db)):
    existing_property = await crud.get_property(db, property.uid)
    if existing_property:
        raise HTTPException(status_code=400, detail="Property with this UID already exists")

    if (property.type == "list" and not property.values) and (property.type == "int" and type(property.values) != int):
        raise HTTPException(status_code=400, detail="error values type")

    return await crud.create_property(db, property)


@router.delete("/{property_uid}")
async def delete_property(property_uid: str, db: AsyncSession = Depends(get_db)):
    property = await crud.delete_property(db, property_uid)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Property deleted successfully"}