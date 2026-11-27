"""Root pytest configuration: fixtures, browser lifecycle and failure screenshots."""

import pytest

# Use the operating system's certificate store for HTTPS (requests and ssl),
# so corporate TLS-inspection proxies work without disabling verification.
try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:  # pragma: no cover - optional dependency
    pass

from playwright.sync_api import sync_playwright  # noqa: E402

from config import settings  # noqa: E402
from pages.auth_pages import LoginPage
from utils.api_client import ApiClient
from utils.data_factory import account_payload, unique_email, unique_name


# ---------------------------------------------------------------------------
# Failure screenshots and HTML report hooks
# ---------------------------------------------------------------------------
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed and "page" in item.funcargs:
        settings.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        path = settings.SCREENSHOTS_DIR / f"{item.name}.png"
        try:
            item.funcargs["page"].screenshot(path=str(path), full_page=True)
            report.sections.append(("Failure screenshot", str(path.relative_to(settings.PROJECT_ROOT))))
        except Exception as exc:  # the browser may already be closed
            report.sections.append(("Failure screenshot", f"not captured: {exc}"))


def pytest_configure(config):
    settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    settings.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Browser fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance):
    launcher = getattr(playwright_instance, settings.BROWSER)
    browser = launcher.launch(headless=settings.HEADLESS, slow_mo=settings.SLOW_MO)
    yield browser
    browser.close()


@pytest.fixture
def context(browser):
    context = browser.new_context(
        viewport=settings.VIEWPORT,
        base_url=settings.BASE_URL,
        ignore_https_errors=True,
    )
    context.set_default_timeout(settings.DEFAULT_TIMEOUT_MS)
    context.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT_MS)
    yield context
    context.close()


@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def login_page(page) -> LoginPage:
    return LoginPage(page)


# ---------------------------------------------------------------------------
# API fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def api() -> ApiClient:
    return ApiClient()


@pytest.fixture
def disposable_user(api):
    """Creates a unique account through the API and deletes it after the test.

    Yields a dict with ``name``, ``email`` and ``password``. Cleanup runs even
    when the test fails, so no test data is left behind on the shared site.
    """
    name = unique_name()
    email = unique_email()
    password = settings.TEST_PASSWORD
    response = api.create_account(account_payload(name, email, password))
    if response.response_code != 201:
        pytest.fail(
            f"Setup failed: could not create disposable user. "
            f"HTTP {response.status_code}, body: {response.raw_text[:300]}"
        )
    user = {"name": name, "email": email, "password": password}
    try:
        yield user
    finally:
        cleanup = api.delete_account(email, password)
        if cleanup.response_code != 200:
            print(f"\n[cleanup warning] could not delete {email}: {cleanup.raw_text[:200]}")
