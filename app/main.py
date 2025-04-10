import json
from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.view.catalog import router as catalog_router
from app.view.products import router as products_router
from app.view.properties import router as properties_router
from db.db import get_db
from service import crud

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog_router, prefix="/catalog", tags=["catalog"])
app.include_router(products_router, prefix="/product", tags=["products"])
app.include_router(properties_router, prefix="/properties", tags=["properties"])

@app.post("/load-test-data/")
async def load_test_data(db: AsyncSession = Depends(get_db)):
    test_data_path = Path(__file__).parent.parent / "test-dump.json"
    with open(test_data_path) as f:
        test_data = json.load(f)

    await crud.load_test_data(db, test_data)
    return {"message": "Test data loaded successfully"}
