from pydantic import BaseModel, ConfigDict

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int

class ProductUpdate(BaseModel):
    name: str
    description: str
    price: float
    stock: int

class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)