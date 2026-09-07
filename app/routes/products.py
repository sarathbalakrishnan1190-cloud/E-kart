from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.redis import redis_client
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductRead
from app.auth import get_current_user, require_admin
import json

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# =========================
# CREATE PRODUCT
# =========================

@router.post("/")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        owner_id=current_user.id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# =========================
# READ ALL PRODUCTS
# =========================

@router.get("/", response_model=list[ProductRead])
def get_products(
    # Filtering
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str | None = None,
    # Pagination
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = select(Product)

    # Search by product name
    if search is not None:
        query = query.where(
            Product.name.ilike(f"%{search}%")
        )

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)
    # sorting
    if sort == "price_asc":
        query = query.order_by(Product.price)
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())

    products = db.execute(
        query.offset(skip)
        .limit(limit)
    ).scalars().all()

    return products


# =========================
# READ ONE PRODUCT
# =========================

@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    cache_key = f"product:{product_id}"

    cached_product = redis_client.get(cache_key)

    if cached_product:
        return json.loads(cached_product)

    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    product_data = ProductRead.model_validate(product).model_dump()

    redis_client.set(
        cache_key,
        json.dumps(product_data),
        ex=60
    )

    return product

# =========================
# UPDATE PRODUCT
# =========================

@router.put("/{product_id}")
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.stock = product_data.stock

    db.commit()
    db.refresh(product)

    redis_client.delete(f"product:{product_id}")

    return product


# =========================
# DELETE PRODUCT
# =========================

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    product = db.get(Product, product_id)
        

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    redis_client.delete(f"product:{product_id}")

    return {
        "message": "Product deleted successfully"
    }



