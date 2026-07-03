from fastapi import APIRouter, Depends, HTTPException,Response, status
from sqlalchemy.orm import Session, joinedload
# from pydantic import BaseModel, ConfigDict
from typing import List

from app.database import get_db
from app.models import Product, Inventory, UserRole, Review, User, Category
from app.auth import RoleChecker, get_current_user
from app.schemas import CreateReview, ProductResponse, ProductCreate, ProductUpdate

from app.core.redis import (
    redis_client,
    CACHE_ALL_PRODUCTS,
    CACHE_TIME
)

import json
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/products", tags=["Products & Inventory"])

# ==========================================
# routes
# ==========================================

# 1. get all products(Public/Customer Access)
# Eager load the 1-to-1 inventory relationship
@router.get("/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """Fetch all products and their current inventory stock."""
        
    cache_key = CACHE_ALL_PRODUCTS
    try:
        cached_products = redis_client.get(cache_key)

        if cached_products:
            logger.info("Returning products from Redis")
            return json.loads(cached_products)
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}")


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
            "category_id":p.category_id,
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
    # Save the response in Redis for 5 minutes    
    try:
        redis_client.setex(
            cache_key,
            CACHE_TIME,
            json.dumps(result, default=str)
        )
    except Exception as e:
        logger.warning(f"Could not cache products: {e}")
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
    #category validation
    category = db.get(Category, product_in.category_id)

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )
    
    # 1.create the Product
    new_product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        category_id=product_in.category_id
    )
    try:
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

        try:
            redis_client.delete(CACHE_ALL_PRODUCTS)
        except Exception:
            pass

        db.refresh(new_product)

        return {
            "message": "Product and Inventory created successfully", 
            "product_id": new_product.id
        }
    except Exception:
        db.rollback()
        raise


# 3. update inventory stock (admin only)
@router.put("/{product_id}/inventory")
def update_inventory(
    product_id: int,
    added_stock: int, # Pass a positive number to add stock, negative to reduce
    db: Session = Depends(get_db),
    current_admin = Depends(RoleChecker([UserRole.ADMIN]))
):
    """Admin endpoint to add or remove stock from the warehouse."""
    try:
        inventory = (db.query(Inventory)
                    .filter(Inventory.product_id == product_id)
                    .with_for_update()
                    .first()
        )
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

        try:
            redis_client.delete(CACHE_ALL_PRODUCTS)
        except Exception:
            pass

        db.refresh(inventory)
        
        return {
            "message": "Inventory successfully updated", 
            "new_total_stock": inventory.stock
        }
    except Exception:
        db.rollback()
        raise

#update a product(admin)
@router.put("/{product_id}", status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,#product to update
    product_up: ProductUpdate,#product fields to update
    db: Session=Depends(get_db),#database session,
    curr_admin: User=Depends(RoleChecker([UserRole.ADMIN]))#Role Based Access Control
):
    """Update the product info"""
    #1. check if product exist
    product_exist=db.get(Product,product_id)
    if not product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    #this will overwrite with None if any field is omitted
    # product_exist.id=product_id
    # product_exist.name=product_up.name
    # product_exist.description=product_up.description
    # product_exist.price=product_up.price
    # product_exist.category_id=product_up.category_id
    update_data = product_up.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(product_exist, key, value)

    db.commit()

    try:
        redis_client.delete(CACHE_ALL_PRODUCTS)
    except Exception:
        pass

    db.refresh(product_exist)

    return {
        "message": "Product updated successfully",
        "product": product_exist
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

#Delete Product(admin)
@router.delete("/{p_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(
    p_id:int,
    db: Session = Depends(get_db),
    curr_admin: User=Depends(RoleChecker([UserRole.ADMIN]))
    ):
    prod=db.get(Product,p_id)
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id:{p_id} not found",
        )
    db.delete(prod)
    db.commit()
    
    try:
        redis_client.delete(CACHE_ALL_PRODUCTS)
    except Exception:
        pass

    return Response(status_code=status.HTTP_204_NO_CONTENT)