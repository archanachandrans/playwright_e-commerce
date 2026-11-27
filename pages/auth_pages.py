"""Page objects for the signup/login page, the signup form and the
account-created / account-deleted confirmation pages."""

import re
from dataclasses import dataclass

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage


@dataclass
class AccountDetails:
    """Data needed to fill the full registration form."""

    name: str
    email: str
    password: str
    title: str = "Mr"                 # "Mr" or "Mrs"
    day: str = "10"
    month: str = "May"
    year: str = "1990"
    first_name: str = "Capstone"
    last_name: str = "Tester"
    company: str = "Capstone QA"
    address: str = "1 Test Street"
    country: str = "India"
    state: str = "Karnataka"
    city: str = "Bengaluru"
    zipcode: str = "560001"
    mobile: str = "0000000000"


class LoginPage(BasePage):
    """Login / signup landing page at /login."""

    INVALID_LOGIN_MESSAGE = "Your email or password is incorrect!"
    SIGNUP_EXISTS_MESSAGE = "Email Address already exist!"

    def __init__(self, page):
        super().__init__(page)
        self.login_email = page.locator("[data-qa='login-email']")
        self.login_password = page.locator("[data-qa='login-password']")
        self.login_button = page.locator("[data-qa='login-button']")
        self.signup_name = page.locator("[data-qa='signup-name']")
        self.signup_email = page.locator("[data-qa='signup-email']")
        self.signup_button = page.locator("[data-qa='signup-button']")
        self.login_heading = page.get_by_role("heading", name="Login to your account")
        self.signup_heading = page.get_by_role("heading", name="New User Signup!")

    def load(self) -> "LoginPage":
        self.open("/login")
        return self

    def login(self, email: str, password: str) -> None:
        self.login_email.fill(email)
        self.login_password.fill(password)
        self.login_button.click()

    def start_signup(self, name: str, email: str) -> None:
        self.signup_name.fill(name)
        self.signup_email.fill(email)
        self.signup_button.click()

    def login_error(self) -> Locator:
        return self.page.locator("form").filter(has=self.login_email).locator("p", has_text=self.INVALID_LOGIN_MESSAGE)

    def signup_error(self) -> Locator:
        return self.page.locator("form").filter(has=self.signup_email).locator("p", has_text=self.SIGNUP_EXISTS_MESSAGE)


class SignupPage(BasePage):
    """Full 'Enter Account Information' form reached after the first signup step."""

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name=re.compile("Enter Account Information", re.IGNORECASE))
        self.title_radio = lambda title: page.locator(f"#id_gender{1 if title == 'Mr' else 2}")
        self.password = page.locator("#password")
        self.day = page.locator("#days")
        self.month = page.locator("#months")
        self.year = page.locator("#years")
        self.newsletter = page.locator("#newsletter")
        self.offers = page.locator("#optin")
        self.first_name = page.locator("#first_name")
        self.last_name = page.locator("#last_name")
        self.company = page.locator("#company")
        self.address = page.locator("#address1")
        self.country = page.locator("#country")
        self.state = page.locator("#state")
        self.city = page.locator("#city")
        self.zipcode = page.locator("#zipcode")
        self.mobile = page.locator("#mobile_number")
        self.create_button = page.locator("[data-qa='create-account']")

    def fill_and_submit(self, data: AccountDetails) -> None:
        self.title_radio(data.title).check()
        self.password.fill(data.password)
        self.day.select_option(data.day)
        self.month.select_option(data.month)
        self.year.select_option(data.year)
        self.newsletter.check()
        self.offers.check()
        self.first_name.fill(data.first_name)
        self.last_name.fill(data.last_name)
        self.company.fill(data.company)
        self.address.fill(data.address)
        self.country.select_option(data.country)
        self.state.fill(data.state)
        self.city.fill(data.city)
        self.zipcode.fill(data.zipcode)
        self.mobile.fill(data.mobile)
        self.create_button.click()


class AccountCreatedPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.heading = page.locator("[data-qa='account-created']")
        self.continue_button = page.locator("[data-qa='continue-button']")

    def is_created(self) -> bool:
        return self.heading.is_visible()

    def expect_created(self) -> None:
        expect(self.heading).to_be_visible()
        # The site displays "Account Created!" and uses CSS to uppercase it.
        expect(self.heading).to_have_text(re.compile("account created!", re.IGNORECASE))

    def continue_to_home(self) -> None:
        self.continue_button.click()


class AccountDeletedPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.heading = page.locator("[data-qa='account-deleted']")

    def expect_deleted(self) -> None:
        expect(self.heading).to_be_visible()
        expect(self.heading).to_have_text(re.compile("account deleted!", re.IGNORECASE))
