import re

from playwright.sync_api import Locator, Page, expect
from config import settings

class BasePage:
    """Common navigation and helper behaviour for all page objects."""

    def __init__(self, page: Page):
        self.page = page

    def open(self, path: str = "/") -> None:
        self.page.goto(f"{settings.BASE_URL}{path}", wait_until="domcontentloaded")

    @property
    def current_path(self) -> str:
        return re.sub(r"^https?://[^/]+", "", self.page.url).split("?")[0]

    # ----- header navigation (present on every page) -----------------------
    def click_nav(self, label: str) -> None:
        # Only visible links: the header can contain hidden duplicates (e.g. responsive menus).
        self.page.locator("header#header li a:visible").filter(has_text=label).first.click()

    def go_to_products(self) -> None:
        self.click_nav("Products")

    def go_to_cart(self) -> None:
        self.click_nav("Cart")

    def go_to_signup_login(self) -> None:
        self.click_nav("Signup / Login")

    def logout_link(self) -> Locator:
        return self.page.locator("header#header").get_by_role("link", name="Logout")

    def logged_in_as(self) -> Locator:
        return self.page.locator("header#header li:has-text('Logged in as') b")

    # ----- generic helpers -------------------------------------------------
    def is_logged_in(self) -> bool:
        return self.logout_link().count() > 0

    def expect_path(self, path: str) -> None:
        expect(self.page).to_have_url(re.compile(rf"{re.escape(settings.BASE_URL)}{re.escape(path)}/?$"))

    def scroll_into_view(self, locator: Locator) -> None:
        locator.scroll_into_view_if_needed()
