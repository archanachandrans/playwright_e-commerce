"""API tests for product and brand endpoints (API scenarios 1-3 and related negatives).

Reference: https://automationexercise.com/api_list
"""

import pytest

from config import settings

pytestmark = pytest.mark.api


def test_get_all_products_list(api):
    """API 1: GET /api/productsList returns the full product catalogue."""
    response = api.get_products()

    assert response.status_code == 200, response.raw_text
    assert response.response_code == 200
    assert isinstance(response.body.get("products"), list)
    assert len(response.body["products"]) > 0


def test_products_list_has_expected_fields(api):
    """Every product in the catalogue exposes the documented fields."""
    products = api.get_products().body["products"]
    required = {"id", "name", "price", "brand", "category"}

    for product in products:
        missing = required - product.keys()
        assert not missing, f"Product {product.get('id')} is missing fields: {missing}"


def test_get_all_brands_list(api):
    """API 2: GET /api/brandsList returns all brands."""
    response = api.get_brands()

    assert response.status_code == 200, response.raw_text
    assert response.response_code == 200
    brands = response.body.get("brands")
    assert isinstance(brands, list) and brands, "brands list is empty or missing"
    assert all("brand" in brand or "name" in brand or "id" in brand for brand in brands)


def test_search_product_returns_matches(api):
    """API 3: POST /api/searchProduct with a valid search term returns matching products."""
    response = api.search_product(settings.SEARCH_TERM)

    assert response.status_code == 200, response.raw_text
    assert response.response_code == 200
    products = response.body.get("products")
    assert isinstance(products, list) and products, f"No products for '{settings.SEARCH_TERM}'"
    assert any(settings.SEARCH_TERM.lower() in p["name"].lower() for p in products)


@pytest.mark.parametrize("term", ["dress", "tshirt", "jeans"])
def test_search_product_multiple_terms(api, term):
    """Parametrised search: each term returns a successful response with a products array."""
    response = api.search_product(term)

    assert response.response_code == 200, response.raw_text
    assert isinstance(response.body.get("products"), list)


def test_search_product_without_parameter_returns_400(api):
    """Negative 1: POST /api/searchProduct without the search_product parameter is rejected."""
    response = api.search_product(None)

    assert response.response_code == 400, response.raw_text  # the API reports 400 inside its JSON body
    assert "search_product" in (response.message or "").lower()
    assert "products" not in response.body
