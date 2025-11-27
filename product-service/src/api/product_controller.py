from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from schemas.product import ProductCreate, ProductRead, ProductUpdate
from repository.product_repository import ProductRepository
from service.product_service import ProductService
from core.database import get_session

router = APIRouter(prefix="/products", tags=["Products"])

# Dependency injection
def get_repo(session: Session = Depends(get_session)) -> ProductRepository:
    return ProductRepository(session)

def get_service(repo: ProductRepository = Depends(get_repo)) -> ProductService:
    return ProductService(repo)

# Create a product
@router.post("/", response_model=ProductRead)
def create_product(
    data: ProductCreate,
    service: ProductService = Depends(get_service)
):
    return service.create_product(data)

# List all products
@router.get("/", response_model=list[ProductRead])
def list_products(service: ProductService = Depends(get_service)):
    return service.list_products()

# Get a single product
@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, service: ProductService = Depends(get_service)):
    product = service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update a product
@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    data: ProductUpdate,
    service: ProductService = Depends(get_service)
):
    product = service.update_product(product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Delete a product
@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, service: ProductService = Depends(get_service)):
    success = service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None
