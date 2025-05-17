from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.category import Category as CategoryModel
from app.schemas.category import CategoryCreate, CategoryUpdate

def get_category(db: Session, category_id: int) -> Optional[CategoryModel]:
    """
    Retrieves a single category by its ID.
    """
    return db.query(CategoryModel).filter(CategoryModel.id == category_id).first()

def get_category_by_name(db: Session, name: str) -> Optional[CategoryModel]:
    """
    Retrieves a single category by its name. Useful for checking uniqueness.
    """
    return db.query(CategoryModel).filter(CategoryModel.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[CategoryModel]:
    """
    Retrieves a list of categories with pagination.
    """
    return db.query(CategoryModel).offset(skip).limit(limit).all()

def create_category(db: Session, category: CategoryCreate) -> CategoryModel:
    """
    Creates a new category in the database.
    """
    db_category = CategoryModel(
        name=category.name,
        description=category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category) 
    return db_category

def update_category(db: Session, db_category: CategoryModel, category_in: CategoryUpdate) -> Optional[CategoryModel]:
    """
    Updates an existing category.
    """
    # 
    update_data = category_in.model_dump(exclude_unset=True)

    if not update_data:
        return db_category 

    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.add(db_category) 
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> Optional[CategoryModel]:
    """
    Deletes a category by its ID.
    """
    db_category = get_category(db=db, category_id=category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
        return db_category
    return None