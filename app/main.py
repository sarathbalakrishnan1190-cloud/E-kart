from fastapi import FastAPI, Request
from app.models.user import User
from app.database import SessionLocal, engine, Base
from app.routes import products
from sqlalchemy.orm import Session
from app.routes import users
from app.routes import cart
from celery.result import AsyncResult
from app.tasks import send_order_notification
from fastapi.responses import JSONResponse
import logging
from app.celery_app import celery_app
from app.routes import orders
from app.routes import payments
from app.redis import redis_client
import os

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

@app.get("/test-task")
def test_task():
    task = send_order_notification.delay(123)

    return {
        "message": "Order notification task sent!",
        "task_id": task.id
    }

@app.get("/task-status/{task_id}")
def task_status(task_id: str):

    result = AsyncResult(
        task_id,
        app=celery_app
    )

    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result
    }



@app.get("/instance")
def instance():
    return {
        "hostname": os.getenv("HOSTNAME")
    }