"""Page objects for products, product details, categories, brands and cart."""

import re

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class ProductsPage(BasePage):
    """/products listing, search, and category/brand listing pages."""

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.locator(".features_items h2.title")
        self.search_input = page.locator("#search_product")
        self.search_button = page.locator("#submit_search")
        self.search_heading = page.get_by_role("heading", name="Searched Products")
        self.product_cards = page.locator(".features_items .product-image-wrapper")
        self.product_names = page.locator(".features_items .product-image-wrapper .productinfo p")
        self.product_prices = page.locator(".features_items .product-image-wrapper .productinfo h2")
        self.view_product_links = page.locator(".features_items a[href^='/product_details/']")
        self.add_to_cart_buttons = page.locator(".features_items .add-to-cart")
        self.brands_sidebar = page.locator(".brands_products")
        self.category_sidebar = page.locator("#accordian")

    def load(self) -> "ProductsPage":
        self.open("/products")
        return self

    def search(self, term: str) -> None:
        self.search_input.fill(term)
        self.search_button.click()

    def product_names_list(self) -> list[str]:
        return [text.strip() for text in self.product_names.all_inner_texts()]

    def view_product(self, index: int = 0) -> None:
        self.view_product_links.nth(index).click()

    def product_card_by_name(self, name: str) -> Locator:
        return self.product_cards.filter(has_text=name).first

    def add_product_to_cart_from_listing(self, name: str) -> None:
        card = self.product_card_by_name(name)
        card.hover()
        card.locator(".add-to-cart").first.click()

    def open_category(self, category: str, sub_category: str) -> None:
        """Expand a category in the sidebar (e.g. 'Women', 'Dress') and open the sub-category link."""
        self.category_sidebar.locator(f"a[href='#{category}']").first.click()
        self.category_sidebar.locator(f"#{category} a", has_text=sub_category).first.click()

    def open_brand(self, brand: str) -> None:
        self.brands_sidebar.get_by_role("link", name=re.compile(rf"\s*{re.escape(brand)}\s*$")).first.click()

    def brand_links(self) -> Locator:
        return self.brands_sidebar.locator("a[href^='/brand_products/']")

    def category_links(self) -> Locator:
        return self.category_sidebar.locator("a[href^='/category_products/']")


class CategoryPage(BasePage):
    """Category listing such as /category_products/1 (Women > Dress)."""

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.locator(".features_items h2.title")
        self.product_names = page.locator(".features_items .product-image-wrapper .productinfo p")


class BrandPage(BasePage):
    """Brand listing such as /brand_products/Polo."""

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.locator(".features_items h2.title")
        self.product_names = page.locator(".features_items .product-image-wrapper .productinfo p")


class ProductDetailPage(BasePage):
    """/product_details/<id> page."""

    def __init__(self, page):
        super().__init__(page)
        self.name = page.locator(".product-information h2")
        self.category = page.locator(".product-information p", has_text="Category:")
        self.price = page.locator(".product-information span span")
        self.availability = page.locator(".product-information p", has_text="Availability:")
        self.condition = page.locator(".product-information p", has_text="Condition:")
        self.brand = page.locator(".product-information p", has_text="Brand:")
        self.quantity_input = page.locator("#quantity")
        self.add_to_cart_button = page.locator("button.cart")
        self.review_name = page.locator("#name")

    def load(self, product_id: int) -> "ProductDetailPage":
        self.open(f"/product_details/{product_id}")
        return self

    def set_quantity(self, quantity: int) -> None:
        self.quantity_input.fill(str(quantity))

    def add_to_cart(self, quantity: int | None = None) -> None:
        if quantity is not None:
            self.set_quantity(quantity)
        self.add_to_cart_button.click()


class CartModal:
    """The confirmation modal that appears after 'Add to cart' on a product page."""

    def __init__(self, page):
        self.modal = page.locator("#cartModal")
        self.view_cart_link = self.modal.get_by_role("link", name="View Cart")
        self.continue_shopping = self.modal.get_by_role("button", name="Continue Shopping")

    def expect_visible(self) -> None:
        expect(self.modal).to_be_visible()

    def go_to_cart(self) -> None:
        self.view_cart_link.click()


class CartPage(BasePage):
    """/view_cart page."""

    EMPTY_CART_TEXT = "Cart is empty!"

    def __init__(self, page):
        super().__init__(page)
        self.rows = page.locator("#cart_info_table tbody tr")
        self.empty_message = page.locator("#empty_cart")
        self.empty_cart_link = page.locator("#empty_cart a[href='/products']")

    def load(self) -> "CartPage":
        self.open("/view_cart")
        return self

    def row_for_product(self, name: str) -> Locator:
        return self.rows.filter(has=self.page.locator(".cart_description h4 a", has_text=name))

    def product_names(self) -> list[str]:
        return [text.strip() for text in self.page.locator(".cart_description h4 a").all_inner_texts()]

    def quantity_of(self, name: str) -> str:
        return self.row_for_product(name).locator(".cart_quantity button").inner_text().strip()

    def price_of(self, name: str) -> str:
        return self.row_for_product(name).locator(".cart_price p").inner_text().strip()

    def total_of(self, name: str) -> str:
        return self.row_for_product(name).locator(".cart_total p").inner_text().strip()

    def remove_product(self, name: str) -> None:
        self.row_for_product(name).locator("a.cart_quantity_delete").click()

    def item_count(self) -> int:
        return self.rows.count()
