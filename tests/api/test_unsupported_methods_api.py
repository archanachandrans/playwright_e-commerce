"""Negative API tests: documented unsupported HTTP methods.

Only the methods the API list explicitly calls out as unsupported are tested.
The documentation says POST on /api/productsList and PUT on /api/brandsList are
not supported, and the expected response is HTTP 200 with an embedded
``responseCode`` of 405 and the message "This request method is not supported.".

Reference: https://automationexercise.com/api_list
"""

import pytest

pytestmark = pytest.mark.api


@pytest.mark.parametrize(
    "method, endpoint",
    [
        ("post", "/api/productsList"),
        ("put", "/api/brandsList"),
    ],
    ids=["POST-productsList", "PUT-brandsList"],
)
def test_documented_unsupported_method_returns_405(api, method, endpoint):
    response = getattr(api, method)(endpoint)

    assert response.response_code == 405, (
        f"{method.upper()} {endpoint}: expected embedded responseCode 405, got "
        f"HTTP {response.status_code} / body {response.raw_text[:300]}"
    )
    assert response.message == "This request method is not supported."
