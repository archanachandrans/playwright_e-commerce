"""UI tests for registration, login and logout (scenarios 2-6).

Reference: https://automationexercise.com/test_cases (Test Cases 1, 2, 4, 5 and 6)
"""

import re

import pytest
from playwright.sync_api import expect

from config import settings
from pages.account_pages import AccountPage
from pages.auth_pages import AccountCreatedPage, AccountDeletedPage, AccountDetails, LoginPage, SignupPage
from pages.home_page import HomePage
from utils.data_factory import account_payload, unique_email, unique_name

pytestmark = pytest.mark.ui


@pytest.fixture
def ui_signup_email(api):
    """Unique e-mail for a UI signup; the account is deleted via the API after the test.

    Cleanup is a no-op when the test never reached account creation (the API
    simply reports 'Account not found').
    """
    email = unique_email("ui_signup")
    yield email
    api.delete_account(email, settings.TEST_PASSWORD)


def test_register_new_user(page, ui_signup_email):
    """Scenario 2 + 3: register a new user and verify the account is created."""
    name = unique_name("UiSignup")
    login = LoginPage(page).load()
    login.start_signup(name, ui_signup_email)

    signup = SignupPage(page)
    # Wait for a form field rather than the heading: the shared site can be slow to render this step.
    expect(signup.password).to_be_visible(timeout=30_000)
    details = AccountDetails(name=name, email=ui_signup_email, password=settings.TEST_PASSWORD)
    signup.fill_and_submit(details)

    created = AccountCreatedPage(page)
    created.expect_created()
    created.continue_to_home()
    expect(AccountPage(page).logged_in_as()).to_have_text(name)


def test_login_with_valid_credentials(page, disposable_user):
    """Scenario 4: login with a valid, pre-registered disposable account."""
    login = LoginPage(page).load()
    login.login(disposable_user["email"], disposable_user["password"])

    home = HomePage(page)
    expect(home.page.locator("header#header li:has-text('Logged in as')")).to_be_visible()
    expect(AccountPage(page).logged_in_as()).to_have_text(disposable_user["name"])
    assert home.is_logged_in()


@pytest.mark.parametrize(
    "email_kind, password_kind",
    [
        ("unknown", "wrong"),
        ("valid", "wrong"),
        ("unknown", "valid"),
    ],
    ids=["unknown-email-wrong-password", "valid-email-wrong-password", "unknown-email-valid-password"],
)
def test_login_with_invalid_credentials(page, disposable_user, email_kind, password_kind):
    """Scenario 5: invalid credential combinations show the documented error."""
    email = disposable_user["email"] if email_kind == "valid" else unique_email("nobody")
    password = disposable_user["password"] if password_kind == "valid" else "NotTheRightPass#1"

    login = LoginPage(page).load()
    login.login(email, password)

    expect(login.login_error()).to_be_visible()
    expect(login.login_heading).to_be_visible()
    assert "/login" in page.url
    assert not AccountPage(page).is_logged_in()


def test_logout(page, disposable_user):
    """Scenario 6: a logged-in user can log out and is returned to the logged-out state."""
    login = LoginPage(page).load()
    login.login(disposable_user["email"], disposable_user["password"])
    account = AccountPage(page)
    expect(account.logged_in_as()).to_have_text(disposable_user["name"])

    account.logout()

    account.expect_logged_out()
    expect(page).to_have_url(re.compile(r"/login$"))


def test_delete_account_via_ui(page, api):
    """Supporting check: the UI delete-account flow removes a disposable account.

    This also serves as cleanup for the account, so no API fixture is needed.
    """
    name = unique_name("UiDelete")
    email = unique_email("ui_delete")
    created = api.create_account(account_payload(name, email))
    assert created.response_code == 201, created.raw_text

    login = LoginPage(page).load()
    login.login(email, settings.TEST_PASSWORD)
    account = AccountPage(page)
    expect(account.logged_in_as()).to_have_text(name)
    account.delete_account()

    AccountDeletedPage(page).expect_deleted()
    assert api.verify_login(email, settings.TEST_PASSWORD).response_code == 404


def test_signup_with_existing_email_shows_error(page, disposable_user):
    """Negative UI check: signing up with an e-mail that already exists is rejected."""
    login = LoginPage(page).load()
    login.start_signup(unique_name("Dup"), disposable_user["email"])

    expect(login.signup_error()).to_be_visible()
