from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import CartItemAdd
from app.database import get_db
from app.models import User, Product, CartItem
from app.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_in: CartItemAdd,  # pydantic validates product_id and quantity>=1
    db: Session = Depends(get_db),
    curr_user: User = Depends(get_current_user),  # must be logged in!
):
    """Add a product to the user's shopping cart"""

    # 1. verify if product exists
    product_exist = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found."
        )

    # 2. check if the item is already in user's cart
    cart_item_exist = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == curr_user.id, CartItem.product_id == item_in.product_id
        )
        .first()
    )
    if cart_item_exist:
        # if item already there, just add to the quantity
        cart_item_exist.quantity += item_in.quantity
    else:
        # if item not there, create a brand new cart_item
        new_cart_item = CartItem(
            user_id=curr_user.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity,
        )
        db.add(new_cart_item)

    # 3. commit the transaction to the database
    db.commit()

    return {"message": f"successfully added {item_in.quantity} item(s) to your cart."}
