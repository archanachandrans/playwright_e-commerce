"""Generates unique, disposable test data.

Every account uses a unique e-mail so that tests never collide with each other
or with accounts created by other people using the shared practice site.
"""

import uuid

from config import settings


def unique_email(prefix: str = "capstone") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}@{settings.TEST_EMAIL_DOMAIN}"


def unique_name(prefix: str = "CapstoneUser") -> str:
    return f"{prefix}{uuid.uuid4().hex[:6]}"


def account_payload(name: str, email: str, password: str | None = None) -> dict:
    """Form payload accepted by POST /api/createAccount (synthetic, non-personal values)."""
    return {
        "name": name,
        "email": email,
        "password": password or settings.TEST_PASSWORD,
        "title": "Mr",
        "birth_date": "10",
        "birth_month": "5",
        "birth_year": "1990",
        "firstname": "Capstone",
        "lastname": "Tester",
        "company": "Capstone QA",
        "address1": "1 Test Street",
        "address2": "Suite 1",
        "country": "India",
        "zipcode": "560001",
        "state": "Karnataka",
        "city": "Bengaluru",
        "mobile_number": "0000000000",
    }
