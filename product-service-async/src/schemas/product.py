from pydantic import BaseModel

class ProductCreate(BaseModel):
    uuid: str
    name: str
    weight: float

class ProductRead(BaseModel):
    id: int
    uuid: str
    name: str
    weight: float

class ProductUpdate(BaseModel):
    uuid: str
    name: str
    weight: float

