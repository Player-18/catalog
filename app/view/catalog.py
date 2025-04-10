from fastapi import APIRouter, Depends, Query
from typing import Optional, Dict, List, Union
from sqlalchemy.ext.asyncio import AsyncSession
import schemas
from db.db import get_db
from service import crud

router = APIRouter()


def parse_filters(params: Dict[str, Union[str, List[str]]]):
    filters = {}
    for key, value in params.items():
        if key.startswith("property_"):
            prop_uid = key[len("property_"):]

            if prop_uid.endswith("_from"):
                prop_uid = prop_uid[:-5]
                if prop_uid not in filters:
                    filters[prop_uid] = {}
                filters[prop_uid]["from"] = int(value)
            elif prop_uid.endswith("_to"):
                prop_uid = prop_uid[:-3]
                if prop_uid not in filters:
                    filters[prop_uid] = {}
                filters[prop_uid]["to"] = int(value)
            else:
                if prop_uid not in filters:
                    filters[prop_uid] = []
                if isinstance(value, list):
                    filters[prop_uid].extend(value)
                else:
                    filters[prop_uid].append(value)
    return filters


@router.get("/", response_model=schemas.ProductListResponse)
async def get_catalog(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        name: Optional[str] = None,
        sort: str = Query("uid", regex="^(uid|name)$"),
        db: AsyncSession = Depends(get_db),
        **params
):
    filters = parse_filters(params)

    skip = (page) * page_size

    products, total = await crud.get_products(
        db, skip=skip, limit=page_size, name=name, filters=filters, sort=sort)

    # Convert to response format
    product_responses = []
    for product in products:
        properties = []
        for prop in product.properties:
            prop_data = {
                "uid": prop.property_uid,
                "name": prop.property.name,
                "value": prop.property.values,
            }
            properties.append(prop_data)

        product_responses.append({
            "uid": product.uid,
            "name": product.name,
            "properties": properties
        })

    return {"products": product_responses, "count": total}


@router.get("/filter/", response_model=schemas.FilterResponse)
async def get_filter_options(
        name: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
        **params
):
    filters = parse_filters(params)
    filter_data = await crud.get_filter_data(db, name=name, filters=filters)

    return {
        "count": filter_data["count"],
        "properties": filter_data["properties"]
    }