"""Page object for logged-in account actions that live in the header."""

from playwright.sync_api import expect

from pages.base_page import BasePage


class AccountPage(BasePage):
    """Helpers for actions available to a logged-in user (logout, delete account)."""

    def __init__(self, page):
        super().__init__(page)
        self.delete_account_link = page.locator("header#header").get_by_role("link", name="Delete Account")

    def logout(self) -> None:
        self.logout_link().click()

    def expect_logged_out(self) -> None:
        expect(self.page.locator("header#header").get_by_role("link", name="Signup / Login")).to_be_visible()
        expect(self.logout_link()).to_have_count(0)

    def expect_logged_in_as(self, name: str) -> None:
        expect(self.logged_in_as()).to_have_text(name)

    def delete_account(self) -> None:
        self.delete_account_link.click()
