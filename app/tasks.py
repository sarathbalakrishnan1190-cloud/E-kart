from app.celery_app import celery_app


from app.celery_app import celery_app


@celery_app.task(
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True
)
def send_order_notification(order_id):
    print(f"Processing order {order_id}")
    print(f"📧 Email sent successfully for order {order_id}")

    return f"Email sent for order {order_id}"