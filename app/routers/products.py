from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import Query

from app import crud, models, schemas
from app.db.session import get_db

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}},)
@router.post(
    "/",
    response_model=schemas.Product,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new product")
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)):
    """
    Register a new product in the system.
    """
    db_product = crud.crud_product.create_product(db=db, product=product)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {product.category_id} not found.")
    created_product_with_details = crud.crud_product.get_product(db=db, product_id=db_product.id)
    return created_product_with_details

@router.get(
    "/",
    response_model=List[schemas.Product],
    summary="Retrieve a list of products")
def read_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = Query(None, description="Filter by Category ID"),
    low_stock: Optional[bool] = Query(None, description="Filter by low stock status (True/False)") # Add query param
    ,
    db: Session = Depends(get_db)):
    """
    Retrieve a list of products. Includes low stock flag.
    """
    products = crud.crud_product.get_products(
        db, skip=skip, limit=limit, category_id=category_id, low_stock=low_stock)
    return products

@router.get(
    "/{product_id}",
    response_model=schemas.Product,
    summary="Retrieve a specific product by ID")
def read_product(
    product_id: int,
    db: Session = Depends(get_db)):
    """
    Retrieve details for a specific product using its ID.
    """
    db_product = crud.crud_product.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return db_product

@router.patch(
    "/{product_id}",
    response_model=schemas.Product,
    summary="Update a product")
def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: Session = Depends(get_db)):
    """
    Update a product's details. Only provided fields are updated.

    """
    db_product_check = crud.crud_product.get_product(db, product_id=product_id) # Check existence first
    if db_product_check is None:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found")

    updated_product = crud.crud_product.update_product(
        db=db, db_product=db_product_check, product_in=product_in)

    if updated_product is None:
        detail_msg = "Failed to update product."
        if product_in.category_id is not None:
             cat_check = db.query(models.Category).get(product_in.category_id)
             if not cat_check:
                  detail_msg = f"Category with ID {product_in.category_id} not found. Cannot update product."

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail_msg)

    return updated_product

@router.delete(
    "/{product_id}",
    response_model=schemas.Product, 
    summary="Delete a product")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)):
    """
    Delete a product by its ID.
    """
    deleted_product = crud.crud_product.delete_product(db=db, product_id=product_id)
    if deleted_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found")
    return deleted_product
