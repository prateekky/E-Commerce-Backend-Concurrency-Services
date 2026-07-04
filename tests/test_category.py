def test_get_all_categories(client, sample_categories):
    response = client.get("/api/categories/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3

    assert data[0]["category_name"] == "Electronics"

def test_get_category_by_slug(client, sample_categories):
    response = client.get("/api/categories/electronics")

    assert response.status_code == 200

    data = response.json()

    assert data["category_name"] == "Electronics"
    assert data["category_slug"] == "electronics"

def test_get_invalid_category(client):
    response = client.get("/api/categories/invalid")

    assert response.status_code == 404

    assert response.json()["detail"] == "Category not found"

def test_create_product_invalid_category(
    client,
    admin_headers,
):
    payload = {
        "name": "MacBook Pro",
        "description": "Apple Laptop",
        "price": 199999,
        "category_id": 999,
        "initial_stock": 10,
    }

    response = client.post(
        "/api/products/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"