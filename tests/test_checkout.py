from app.models import Inventory, CartItem, Order, OrderStatus


def create_product(client, admin_headers, sample_categories):
    payload = {
        "name": "MacBook Pro",
        "description": "Apple Laptop",
        "price": 199999,
        "category_id": sample_categories[0].id,
        "initial_stock": 10,
    }

    response = client.post(
        "/api/products/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 201

    return response.json()["product_id"]


def test_checkout_empty_cart(
    client,
    customer_headers,
):
    response = client.post(
        "/api/checkout/",
        headers=customer_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Your cart is empty."


def test_successful_checkout(
    client,
    db,
    admin_headers,
    customer_headers,
    customer_user,
    sample_categories,
):
    product_id = create_product(
        client,
        admin_headers,
        sample_categories,
    )

    response = client.post(
        "/api/cart/",
        json={
            "product_id": product_id,
            "quantity": 2,
        },
        headers=customer_headers,
    )

    assert response.status_code == 201

    response = client.post(
        "/api/checkout/",
        headers=customer_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "Checkout custom transaction completed successfully."

    inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == product_id)
        .first()
    )

    assert inventory.stock == 8

    cart_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == customer_user.id)
        .all()
    )

    assert len(cart_items) == 0

    order = (
        db.query(Order)
        .filter(Order.user_id == customer_user.id)
        .first()
    )

    assert order is not None
    assert order.status == OrderStatus.COMPLETED


def test_insufficient_inventory(
    client,
    db,
    admin_headers,
    customer_headers,
    sample_categories,
):
    product_id = create_product(
        client,
        admin_headers,
        sample_categories,
    )

    inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == product_id)
        .first()
    )

    inventory.stock = 1
    db.commit()

    response = client.post(
        "/api/cart/",
        json={
            "product_id": product_id,
            "quantity": 2,
        },
        headers=customer_headers,
    )

    assert response.status_code == 201

    response = client.post(
        "/api/checkout/",
        headers=customer_headers,
    )

    assert response.status_code == 400

    inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == product_id)
        .first()
    )

    assert inventory.stock == 1

    order = db.query(Order).first()

    assert order is None