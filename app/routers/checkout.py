from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import User, CartItem, Inventory, Order, OrderItem, OrderStatus
from app.auth import get_current_user
from decimal import Decimal

router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def checkout_cart(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Submits user cart, verifies and decrements inventory with row-level locks,
    and returns a confirmed order - ensuring complete transactional ACID integrity.
    """
    # 1. Fetch all items in user's active shopping cart with eager loading
    cart_items = (
        db.query(CartItem)
        .options(joinedload(CartItem.product))
        .filter(CartItem.user_id == current_user.id)
        .order_by(
            CartItem.product_id
        )  # Enforces sequential locking order to make deadlock impossible
        .all()
    )
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Your cart is empty."
        )

    order_items_to_create = []
    total_amount = Decimal("0.00")

    try:
        # 2. Iterate and verify inventory with pessimistic lock
        for item in cart_items:
            # Verify product still exists
            if not item.product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product ID {item.product_id} no longer exists",
                )

            # OPTION 1: PESSIMISTIC LOCKING using SQLAlchemy (.with_for_update())
            # This generates a 'SELECT ... FOR UPDATE' row-lock on PostgreSQL.
            # Any concurrent transactions attempting to read/lock this row will halt
            # and wait until this transaction either COMMITs or ROLLBACKs.
            inventory = (
                db.query(Inventory)
                .filter(Inventory.product_id == item.product_id)
                .with_for_update()  # CRITICAL: This is the row-level lock
                .first()
            )

            if not inventory:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Inventory record missing for product ID {item.product_id}",
                )

            # Check if stock is sufficient
            if inventory.stock < item.quantity:
                # If transaction fails, the block triggers a rollback
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Overselling avoided! '{item.product.name}' is out of stock or quantity exceeds availability. Requested: {item.quantity}, Current Stock: {inventory.stock}",
                )

            # Deduct inventory count safely within lock
            inventory.stock -= item.quantity

            # Record pricing and purchase info
            item_price = item.product.price
            total_amount += item_price * item.quantity

            order_items_to_create.append(
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item_price,
                )
            )

        # 3. Create the confirmed parent order
        new_order = Order(
            user_id=current_user.id,
            total_amount=round(total_amount, 2),
            status=OrderStatus.COMPLETED,
        )
        db.add(new_order)
        db.flush()  # Yields order ID without committing yet

        # Attach purchase sub-items
        for order_item in order_items_to_create:
            order_item.order_id = new_order.id
            db.add(order_item)

        # 4. Wipe checkout cart items
        db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()

        # 5. Commit atomic transaction - releasing database row locks!
        db.commit()
        return {
            "message": "Checkout custom transaction completed successfully.",
            "order_id": new_order.id,
            "total_charged": new_order.total_amount,
            "status": new_order.status,
        }

    except Exception as e:
        # Automatic rollback to guarantee database consistency
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected database transaction error occurred: {str(e)}",
        )
