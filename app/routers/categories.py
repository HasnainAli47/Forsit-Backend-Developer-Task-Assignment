from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.db.session import get_db

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    responses={404: {"description": "Not found"}},)

@router.post(
    "/",
    response_model=schemas.Category,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category")
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db)):
    """
    Create a new category.
    """
    db_category = crud.crud_category.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category.name}' already exists."
        )
    return crud.crud_category.create_category(db=db, category=category)

@router.get(
    "/",
    response_model=List[schemas.Category],
    summary="Retrieve a list of categories"
)
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)):
    """
    Retrieve a list of categories with optional pagination.
    """
    categories = crud.crud_category.get_categories(db, skip=skip, limit=limit)
    return categories

@router.get(
    "/{category_id}",
    response_model=schemas.Category,
    summary="Retrieve a specific category by ID")
def read_category(
    category_id: int,
    db: Session = Depends(get_db)):
    """
    Retrieve details for a specific category using its ID.
    """
    db_category = crud.crud_category.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found")
    return db_category

@router.patch(
    "/{category_id}",
    response_model=schemas.Category,
    summary="Update a category"
)
def update_category(
    category_id: int,
    category_in: schemas.CategoryUpdate,
    db: Session = Depends(get_db)):
    """
    Update a category's details. Only provided fields are updated.
    """
    db_category = crud.crud_category.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found")

    if category_in.name and category_in.name != db_category.name:
        existing_category = crud.crud_category.get_category_by_name(db, name=category_in.name)
        if existing_category and existing_category.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category name '{category_in.name}' is already taken."
            )

    updated_category = crud.crud_category.update_category(
        db=db, db_category=db_category, category_in=category_in)
    return updated_category

@router.delete(
    "/{category_id}",
    response_model=schemas.Category,
    summary="Delete a category")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a category by its ID.
    """
    deleted_category = crud.crud_category.delete_category(db=db, category_id=category_id)
    if deleted_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found")
    return deleted_category
