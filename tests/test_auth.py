def test_create_category(client, admin_headers):

    payload = {
        "category_name": "Sports",
        "category_slug": "sports"
    }

    response = client.post(
        "/api/categories/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["category_name"] == "Sports"
    assert data["category_slug"] == "sports"

#duplicacy testing
def test_duplicate_category_slug(client, admin_headers):

    payload = {
        "category_name": "Sports",
        "category_slug": "sports"
    }

    client.post(
        "/api/categories/",
        json=payload,
        headers=admin_headers,
    )

    response = client.post(
        "/api/categories/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == \
        "A category with this slug already exists."
    
#check if customer can post an sports or not
def test_customer_cannot_create_category(
    client,
    customer_headers,
):

    response = client.post(
        "/api/categories/",
        json={
            "category_name": "Sports",
            "category_slug": "sports",
        },
        headers=customer_headers,
    )

    assert response.status_code == 403