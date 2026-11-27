import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.product_pages import (
    BrandPage,
    CartModal,
    CartPage,
    CategoryPage,
    ProductDetailPage,
    ProductsPage,
)
from utils.data_factory import unique_email

pytestmark = pytest.mark.ui

PRODUCT_ID = 1                 # stable public product used across cart tests
SEARCH_TERM = "top"


# ---------------------------------------------------------------------------
# Scenario 1 - home page
# ---------------------------------------------------------------------------
def test_home_page_loads_successfully(page):
    home = HomePage(page).load()

    expect(page).to_have_title(re.compile("Automation Exercise", re.IGNORECASE))
    assert home.is_loaded(), "Home page header or slider did not render"
    expect(page.locator("header#header").get_by_role("link", name="Signup / Login")).to_be_visible()


# ---------------------------------------------------------------------------
# Scenario 7 - products page
# ---------------------------------------------------------------------------
def test_navigate_to_products_page(page):
    HomePage(page).load()
    products = ProductsPage(page)
    products.go_to_products()

    products.expect_path("/products")
    expect(products.heading).to_have_text(re.compile("All Products", re.IGNORECASE))
    assert products.product_cards.count() > 0, "No products listed on the products page"


# ---------------------------------------------------------------------------
# Scenario 8 - search
# ---------------------------------------------------------------------------
def test_search_product_returns_matching_results(page):
    products = ProductsPage(page).load()
    products.search(SEARCH_TERM)

    expect(products.search_heading).to_be_visible()
    names = products.product_names_list()
    assert names, f"Search for '{SEARCH_TERM}' returned no products"
    assert any(SEARCH_TERM.lower() in name.lower() for name in names), (
        f"No product name contains '{SEARCH_TERM}'. Names returned: {names}"
    )


@pytest.mark.parametrize("term", ["zzzz-no-such-product-xyz"], ids=["no-results"])
def test_search_with_no_match_shows_no_products(page, term):
    products = ProductsPage(page).load()
    products.search(term)

    expect(products.search_heading).to_be_visible()
    assert products.product_cards.count() == 0


# ---------------------------------------------------------------------------
# Scenario 9 - product details
# ---------------------------------------------------------------------------
def test_view_product_details(page):
    details = ProductDetailPage(page).load(PRODUCT_ID)

    expect(details.name).to_be_visible()
    assert details.name.inner_text().strip(), "Product name is empty"
    expect(details.category).to_be_visible()
    expect(details.price).to_be_visible()
    expect(details.availability).to_be_visible()
    expect(details.condition).to_be_visible()
    expect(details.brand).to_be_visible()


def test_view_product_details_from_listing(page):
    products = ProductsPage(page).load()
    listed_name = products.product_names_list()[0]
    products.view_product(0)

    details = ProductDetailPage(page)
    expect(details.name).to_have_text(listed_name)
    assert re.search(r"/product_details/\d+", page.url)


# ---------------------------------------------------------------------------
# Scenario 10 - add to cart
# ---------------------------------------------------------------------------
def test_add_product_to_cart_from_details_page(page):
    details = ProductDetailPage(page).load(PRODUCT_ID)
    product_name = details.name.inner_text().strip()

    details.add_to_cart()
    modal = CartModal(page)
    modal.expect_visible()
    modal.go_to_cart()

    cart = CartPage(page)
    expect(page).to_have_url(re.compile(r"/view_cart$"))
    assert product_name in cart.product_names(), f"'{product_name}' missing from cart"


# ---------------------------------------------------------------------------
# Scenario 11 - verify product details and quantity in cart
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("quantity", [1, 4])
def test_cart_shows_correct_product_and_quantity(page, quantity):
    details = ProductDetailPage(page).load(PRODUCT_ID)
    product_name = details.name.inner_text().strip()
    expected_price = details.price.inner_text().strip()

    details.add_to_cart(quantity=quantity)
    CartModal(page).go_to_cart()

    cart = CartPage(page)
    expect(cart.row_for_product(product_name)).to_have_count(1)
    assert cart.quantity_of(product_name) == str(quantity)
    assert cart.price_of(product_name) == expected_price


# ---------------------------------------------------------------------------
# Scenario 12 - remove from cart
# ---------------------------------------------------------------------------
def test_remove_product_from_cart(page):
    details = ProductDetailPage(page).load(PRODUCT_ID)
    product_name = details.name.inner_text().strip()
    details.add_to_cart()
    CartModal(page).go_to_cart()

    cart = CartPage(page)
    expect(cart.row_for_product(product_name)).to_have_count(1)
    cart.remove_product(product_name)

    expect(cart.row_for_product(product_name)).to_have_count(0)
    expect(cart.empty_message).to_be_visible()


# ---------------------------------------------------------------------------
# Scenario 13 - categories
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "category, sub_category, expected_heading",
    [
        ("Women", "Dress", "Women - Dress Products"),
        ("Men", "Tshirts", "Men - Tshirts Products"),
    ],
    ids=["women-dress", "men-tshirts"],
)
def test_navigate_product_categories(page, category, sub_category, expected_heading):
    products = ProductsPage(page).load()
    products.open_category(category, sub_category)

    heading = CategoryPage(page).heading
    expect(heading).to_have_text(re.compile(re.escape(expected_heading), re.IGNORECASE))
    assert CategoryPage(page).product_names.count() > 0


# ---------------------------------------------------------------------------
# Scenario 14 - brands
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("brand", ["Polo", "H&M"], ids=["polo", "h-and-m"])
def test_navigate_product_brands(page, brand):
    products = ProductsPage(page).load()
    products.open_brand(brand)

    brand_page = BrandPage(page)
    expect(page).to_have_url(re.compile(r"/brand_products/"))
    expect(brand_page.heading).to_contain_text(re.compile(re.escape(brand), re.IGNORECASE), timeout=30_000)
    assert brand_page.product_names.count() > 0


# ---------------------------------------------------------------------------
# Scenario 15 - subscription
# ---------------------------------------------------------------------------
def test_subscribe_to_newsletter(page):
    home = HomePage(page).load()
    home.subscribe(unique_email("subscriber"))

    home.expect_subscription_success()
