"""API tests for account endpoints: login verification, create, update, delete and
user lookup (API scenarios 4-8 and login negatives).

Reference: https://automationexercise.com/api_list

All accounts are disposable: each is created with a unique e-mail and deleted at
the end of the test (or by the ``disposable_user`` fixture).
"""

import pytest

from config import settings
from utils.data_factory import account_payload, unique_email, unique_name

pytestmark = pytest.mark.api


# ---------------------------------------------------------------------------
# API 4 - verify login
# ---------------------------------------------------------------------------
def test_verify_login_with_valid_credentials(api, disposable_user):
    response = api.verify_login(disposable_user["email"], disposable_user["password"])

    assert response.status_code == 200, response.raw_text
    assert response.response_code == 200
    assert response.message == "User exists!"


@pytest.mark.parametrize(
    "email_kind, password_kind",
    [("unknown", "wrong"), ("valid", "wrong"), ("unknown", "valid")],
    ids=["unknown-email", "wrong-password", "unknown-email-valid-password"],
)
def test_verify_login_with_invalid_credentials(api, disposable_user, email_kind, password_kind):
    """Negative 2: invalid credential combinations return 404 'User not found!'."""
    email = disposable_user["email"] if email_kind == "valid" else unique_email("nobody")
    password = disposable_user["password"] if password_kind == "valid" else "WrongPass#999"

    response = api.verify_login(email, password)

    assert response.response_code == 404, response.raw_text
    assert response.message == "User not found!"


@pytest.mark.parametrize(
    "email, password",
    [(None, settings.TEST_PASSWORD), ("someone@example.com", None)],
    ids=["missing-email", "missing-password"],
)
def test_verify_login_without_required_fields(api, email, password):
    """Negative 3: email or password missing from the request returns 400."""
    response = api.verify_login(email, password)

    assert response.response_code == 400, response.raw_text
    assert "parameter is missing" in (response.message or "").lower()


def test_verify_login_with_blank_email_observed_behaviour(api):
    """Observed behaviour (not a documented rule): an empty email string is sent as a
    value rather than omitted, so the API reports 'User not found!' (404) instead of
    the 400 'parameter is missing' error. Recorded here so the difference is visible."""
    response = api.verify_login("", settings.TEST_PASSWORD)

    assert response.response_code == 404, response.raw_text
    assert response.message == "User not found!"


# ---------------------------------------------------------------------------
# API 5 - create user account
# ---------------------------------------------------------------------------
def test_create_user_account(api):
    name, email = unique_name("ApiCreate"), unique_email("api_create")
    try:
        response = api.create_account(account_payload(name, email))

        # The API documents 201 in its JSON body (responseCode). The HTTP status line
        # is observed as 200, so only the body code is asserted here.
        assert response.response_code == 201, response.raw_text
        assert response.message == "User created!"
        assert api.verify_login(email, settings.TEST_PASSWORD).response_code == 200
    finally:
        api.delete_account(email, settings.TEST_PASSWORD)


def test_create_account_with_existing_email_fails(api, disposable_user):
    response = api.create_account(
        account_payload(unique_name("Duplicate"), disposable_user["email"], disposable_user["password"])
    )

    assert response.response_code == 400, response.raw_text
    assert response.message == "Email already exists!"


# ---------------------------------------------------------------------------
# API 6 - update user account
# ---------------------------------------------------------------------------
def test_update_user_account(api, disposable_user):
    payload = account_payload(disposable_user["name"] + "Updated", disposable_user["email"],
                              disposable_user["password"])
    payload["company"] = "Updated Capstone QA"

    response = api.update_account(payload)

    assert response.status_code == 200, response.raw_text
    assert response.response_code == 200
    assert response.message == "User updated!"

    details = api.get_user_detail_by_email(disposable_user["email"]).body["user"]
    assert details["company"] == "Updated Capstone QA"


# ---------------------------------------------------------------------------
# API 7 - delete user account
# ---------------------------------------------------------------------------
def test_delete_user_account(api):
    email = unique_email("api_delete")
    assert api.create_account(account_payload(unique_name("ApiDelete"), email)).response_code == 201

    response = api.delete_account(email, settings.TEST_PASSWORD)

    assert response.status_code == 200, response.raw_text
    assert response.response_code == 200
    assert response.message == "Account deleted!"
    assert api.verify_login(email, settings.TEST_PASSWORD).response_code == 404


def test_delete_account_that_does_not_exist(api):
    response = api.delete_account(unique_email("ghost"), settings.TEST_PASSWORD)

    assert response.response_code == 404, response.raw_text
    assert response.message == "Account not found!"


# ---------------------------------------------------------------------------
# API 8 - get user details by email
# ---------------------------------------------------------------------------
def test_get_user_details_by_email(api, disposable_user):
    response = api.get_user_detail_by_email(disposable_user["email"])

    assert response.status_code == 200, response.raw_text
    assert response.response_code == 200
    user = response.body["user"]
    assert user["email"] == disposable_user["email"]
    assert user["name"] == disposable_user["name"]


def test_get_user_details_for_unknown_email(api):
    response = api.get_user_detail_by_email(unique_email("missing"))

    assert response.response_code == 404, response.raw_text
    assert "user" not in response.body
