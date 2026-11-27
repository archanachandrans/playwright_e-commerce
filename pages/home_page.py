from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


class HomePage(BasePage):
    SUBSCRIPTION_HEADING = "Subscription"
    SUBSCRIBE_SUCCESS = "You have been successfully subscribed!"

    def __init__(self, page):
        super().__init__(page)
        self.slider = page.locator("#slider")
        self.subscription_email = page.locator("#susbscribe_email")
        self.subscribe_button = page.locator("#subscribe")
        self.subscribe_alert = page.locator(".alert-success")
        self.category_panel = page.locator("#accordian")
        self.brand_panel = page.locator(".brands-name")

    def load(self) -> "HomePage":
        self.open("/")
        # Wait for the rendered header rather than DOMContentLoaded, which can fire before the page is usable.
        expect(self.page.locator("header#header")).to_be_visible()
        return self

    def is_loaded(self) -> bool:
        return self.slider.is_visible() and self.page.locator("header#header").is_visible()

    def subscribe(self, email: str) -> None:
        self.scroll_into_view(self.subscription_email)
        self.subscription_email.fill(email)
        self.subscribe_button.click()

    def subscription_success_message(self) -> Locator:
        return self.page.locator(".alert-success", has_text=self.SUBSCRIBE_SUCCESS)

    def expect_subscription_success(self) -> None:
        expect(self.subscription_success_message()).to_be_visible()
