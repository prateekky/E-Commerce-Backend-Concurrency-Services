from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.schemas import CategoryResponse, CategoryCreate, CategoryInDB
from app.models import Category, UserRole
from app.database import get_db
from app.auth import RoleChecker

router=APIRouter(prefix="/categories", tags=["Categories"])

#1. get all categories
@router.get("/",response_model=list[CategoryInDB])
async def get_all_categories(
    db:Session=Depends(get_db)
):
    """Fetch all categories without loading products to keep it fast."""
    categories=(
        db.query(Category).all()
    )
    
    return categories

#2. get category by slug + its products
@router.get("/{slug}",response_model=CategoryResponse)
async def get_by_slug(
    slug:str,
    db:Session=Depends(get_db)
):
    """Fetch a specific category and all its associated products."""
    category=(
        db.query(Category)
        .options(joinedload(Category.products))
        .filter(Category.category_slug==slug)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category

# 3. create category(admin)
@router.post("/",response_model=CategoryInDB, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in:CategoryCreate,
    db:Session=Depends(get_db),
    current_admin=Depends(RoleChecker([UserRole.ADMIN]))
):
    """Admin endpoint to create a new category."""
    new_category=Category(
        category_name=category_in.category_name,
        category_slug=category_in.category_slug
    )

    db.add(new_category)
    
    try:
        db.commit()
        db.refresh(new_category)
        return new_category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A category with this slug already exists."
        )