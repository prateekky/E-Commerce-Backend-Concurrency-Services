from app.models import Inventory


def test_get_products_empty(client):
    response = client.get("/api/products/")

    assert response.status_code == 200
    assert response.json() == []


# create product
def test_create_product(client, admin_headers, sample_product_categories, db):

    response = client.post(
        "/api/products/",
        json=sample_product_categories,
        headers=admin_headers,
    )

    assert response.status_code == 201

    product_id = response.json()["product_id"]

    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()

    assert inventory is not None
    assert inventory.stock == 10


# customer forbidden
def test_customer_forbidden(
    client,
    customer_headers,
    sample_product_categories,
):

    response = client.post(
        "/api/products/",
        json=sample_product_categories,
        headers=customer_headers,
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == "You do not have permission to access this resource"
    )
