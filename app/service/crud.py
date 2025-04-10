from sqlalchemy import func, and_, or_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tables import models
import schemas

async def get_property(db: AsyncSession, property_uid: str):
    result = await db.execute(
        select(models.Property).where(models.Property.uid == property_uid))
    return result.scalars().first()


async def create_property(db: AsyncSession, property: schemas.PropertyCreate):
    db_property = models.Property(
        uid=property.uid,
        name=property.name,
        type=property.type,
        values=property.values if type(property.values) == int else [v.dict() for v in property.values]
    )
    db.add(db_property)
    await db.commit()
    await db.refresh(db_property)
    return db_property


async def delete_property(db: AsyncSession, property_uid: str):
    result = await db.execute(
        select(models.Property).where(models.Property.uid == property_uid))
    property = result.scalars().first()
    if property:
        await db.delete(property)
        await db.commit()
    return property


async def get_product(db: AsyncSession, product_uid: str):
    result = await db.execute(
        select(models.Product).where(models.Product.uid == product_uid)        .options(
            selectinload(models.Product.properties)
            .selectinload(models.ProductProperty.property)  # Загружаем связанное свойство
        ))
    return result.scalars().first()


async def get_products(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        name: str = None,
        filters: dict = None,
        sort: str = "uid"
):
    query = select(models.Product).options(
            selectinload(models.Product.properties)
            .selectinload(models.ProductProperty.property)
        )

    if name:
        query = query.where(models.Product.name.ilike(f"%{name}%"))

    if filters:
        for prop_uid, values in filters.items():
            if isinstance(values, dict):  # range filter for int
                subq = select(models.ProductProperty.product_uid).where(
                    models.ProductProperty.property_uid == prop_uid)

                if 'from' in values:
                    subq = subq.where(models.ProductProperty.value >= values['from'])
                if 'to' in values:
                    subq = subq.where(models.ProductProperty.value <= values['to'])

                query = query.where(models.Product.uid.in_(subq))
            else:  # list of values for list property
                subq = select(models.ProductProperty.product_uid).where(
                    and_(
                        models.ProductProperty.property_uid == prop_uid,
                        models.ProductProperty.value_uid.in_(values)
                    )
                )
                query = query.where(models.Product.uid.in_(subq))

    # Sorting
    if sort == "name":
        query = query.order_by(models.Product.name)
    else:
        query = query.order_by(models.Product.uid)

    # Count before pagination
    count_query = select(func.count()).select_from(query)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    return products, total


async def create_product(db: AsyncSession, product: schemas.ProductCreate):
    db_product = models.Product(uid=product.uid, name=product.name)
    db.add(db_product)

    for prop in product.properties:
        db_prop = models.ProductProperty(
            product_uid=product.uid,
            property_uid=prop.uid,
        )
        db.add(db_prop)

    await db.commit()
    await db.refresh(db_product)
    return db_product


async def delete_product(db: AsyncSession, product_uid: str):
    result = await db.execute(
        select(models.Product).where(models.Product.uid == product_uid))
    product = result.scalars().first()
    if product:
        await db.delete(product)
        await db.commit()
    return product


async def get_filter_data(db: AsyncSession, name: str = None, filters: dict = None):
    # Base query to get filtered product IDs
    product_query = select(models.Product.uid)

    if name:
        product_query = product_query.where(models.Product.name.ilike(f"%{name}%"))

    if filters:
        for prop_uid, values in filters.items():
            if isinstance(values, dict):  # range filter
                subq = select(models.ProductProperty.product_uid).where(
                    models.ProductProperty.property_uid == prop_uid)

                if 'from' in values:
                    subq = subq.where(models.ProductProperty.value >= values['from'])
                if 'to' in values:
                    subq = subq.where(models.ProductProperty.value <= values['to'])

                product_query = product_query.where(models.Product.uid.in_(subq))
            else:  # list values
                subq = select(models.ProductProperty.product_uid).where(
                    and_(
                        models.ProductProperty.property_uid == prop_uid,
                        models.ProductProperty.value_uid.in_(values)
                    )
                )
                product_query = product_query.where(models.Product.uid.in_(subq))

    product_result = await db.execute(product_query)
    product_ids = [p[0] for p in product_result.all()]

    count = len(product_ids)

    properties_data = {}

    properties_result = await db.execute(select(models.Property))
    properties = properties_result.scalars().all()

    for prop in properties:
        if prop.type == "list":
            values_data = {}
            for value in prop.values:
                count_query = select(func.count()).where(
                    and_(
                        models.ProductProperty.property_uid == prop.uid,
                        models.ProductProperty.value_uid == value["value_uid"],
                        models.ProductProperty.product_uid.in_(product_ids)
                    )
                )
                value_count = (await db.execute(count_query)).scalar()
                values_data[value["value_uid"]] = value_count

            properties_data[prop.uid] = values_data
        else:
            min_query = select(func.min(models.ProductProperty.value)).where(
                and_(
                    models.ProductProperty.property_uid == prop.uid,
                    models.ProductProperty.product_uid.in_(product_ids)
                ))
            max_query = select(func.max(models.ProductProperty.value)).where(
                and_(
                    models.ProductProperty.property_uid == prop.uid,
                    models.ProductProperty.product_uid.in_(product_ids)
                ))

            min_val = (await db.execute(min_query)).scalar()
            max_val = (await db.execute(max_query)).scalar()

            properties_data[prop.uid] = {
                "min_value": min_val,
                "max_value": max_val
            }

    return {
        "count": count,
        "properties": properties_data
    }


async def load_test_data(db: AsyncSession, data: dict):

    for prop_data in data["properties"]:
        prop = models.Property(
            uid=prop_data["uid"],
            name=prop_data["name"],
            type=prop_data["type"],
            values=[{'value': item['value']} for item in prop_data.get("values")] if prop_data.get("values") else prop_data.get("value")
        )
        db.add(prop)

    for product_data in data["products"]:
        product = models.Product(
            uid=product_data["uid"],
            name=product_data["name"]
        )
        db.add(product)

        for prop_data in product_data["properties"]:
            prop_type = next(
                (p["type"] for p in data["properties"] if p["uid"] == prop_data["uid"]),
                None
            )

            if prop_type == "list":
                product_prop = models.ProductProperty(
                    product_uid=product_data["uid"],
                    property_uid=prop_data["uid"],
                )
            else:
                product_prop = models.ProductProperty(
                    product_uid=product_data["uid"],
                    property_uid=prop_data["uid"],
                )
            db.add(product_prop)

    await db.commit()