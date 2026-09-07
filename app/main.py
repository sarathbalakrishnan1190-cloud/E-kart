from fastapi import FastAPI, Request
from app.models.user import User
from app.database import SessionLocal, engine, Base
from app.routes import products
from sqlalchemy.orm import Session
from app.routes import users
from app.routes import cart

from fastapi.responses import JSONResponse
import logging
from app.routes import orders
from app.routes import payments
from app.redis import redis_client

logger = logging.getLogger(__name__)
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(products.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(cart.router)
app.include_router(payments.router)

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception("Unexpected error")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Something went wrong"
        }
    )
    
@app.get("/redis-test")
def redis_test():
    redis_client.set("message", "Hello from Redis!")
    
    value = redis_client.get("message")
    
    return {
        "message": value
    }