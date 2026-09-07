from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderItemRead(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderRead(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    items: list[OrderItemRead]

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str