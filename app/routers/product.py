from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from app.database import get_db
from app.models import Product, Inventory, UserRole, Review, User
from app.auth import RoleChecker, get_current_user
from app.schemas import CreateReview, ProductResponse, ProductCreate

router = APIRouter(prefix="/products", tags=["Products & Inventory"])

# ==========================================
# routes
# ==========================================

# 1. get all products(Public/Customer Access)
# Eager load the 1-to-1 inventory relationship
@router.get("/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """Fetch all products and their current inventory stock."""
    products = db.query(Product).options(
        joinedload(Product.inventory),
        joinedload(Product.reviews)
        ).all()
    
    result = []
    
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "created_at":p.created_at,
            "stock": p.inventory.stock if p.inventory else 0,
            "reviews":[
                {
                    "rating": r.rating,
                    "comment": r.comment
                }
                for r in p.reviews
            ]
        })
    return result


# 2. create product (ADMIN ONLY - Role-Based Access Control)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate, 
    db: Session = Depends(get_db),
    # THIS is your RBAC in action! Only tokens with 'admin' role can pass this check.
    current_admin = Depends(RoleChecker([UserRole.ADMIN])) 
):
    """Creates a new product and automatically initializes its inventory."""
    
    # 1.create the Product
    new_product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        category_id=product_in.category_id
    )
    db.add(new_product)
    db.flush() # flushes to DB to get the new_product.id without fully committing

    # 2. create the linked Inventory record (1-to-1 relationship)
    new_inventory = Inventory(
        product_id=new_product.id,
        stock=product_in.initial_stock
    )
    db.add(new_inventory)
    
    # 3.commit the transaction
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product and Inventory created successfully", 
        "product_id": new_product.id
    }


# 3. update inventory stock (admin only)
@router.put("/{product_id}/inventory")
def update_inventory(
    product_id: int,
    added_stock: int, # Pass a positive number to add stock, negative to reduce
    db: Session = Depends(get_db),
    current_admin = Depends(RoleChecker([UserRole.ADMIN]))
):
    """Admin endpoint to add or remove stock from the warehouse."""
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Inventory record not found for this product"
        )
    
    if inventory.stock + added_stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )
    inventory.stock += added_stock
    db.commit()
    
    return {
        "message": "Inventory successfully updated", 
        "new_total_stock": inventory.stock
    }

#Post reviews (public/customer)
@router.post("/{product_id}/reviews", status_code=status.HTTP_201_CREATED)
def create_review(
    product_id: int, #Id from URL
    review_in:CreateReview, # Grab JSON body(rating & comment)
    db: Session = Depends(get_db), # database session
    curr_user: User=Depends(get_current_user) #logged-in user
):
    """Add review to the product"""
    #1. check if product exist
    curr_product=db.query(Product).filter(Product.id==product_id).first()
    if not curr_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    #1.5. if already reviewed (optional)

    existing_review=db.query(Review).filter(
        Review.product_id==product_id,
        Review.user_id==curr_user.id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product.")

    #2. create the review object
    new_review=Review(
        product_id=product_id,
        user_id=curr_user.id, # got securely from jwt token!
        rating=review_in.rating,
        comment=review_in.comment
    )

    #3. save to database
    db.add(new_review)
    db.commit()
    db.refresh(new_review) #refresh to get generated review_id and created_at

    return {
        "message": "Review added successfully",
        "review_id": new_review.id
    }

#Delete Product
@router.delete("/{p_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(p_id, db: Session = Depends(get_db)):
    prod=db.get(Product,p_id)
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id:{p_id} not found",
        )
    db.delete(prod)
    db.commit()
    return status.HTTP_204_NO_CONTENT