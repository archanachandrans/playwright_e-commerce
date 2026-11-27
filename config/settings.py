"""Centralised configuration for the Automation Exercise test framework.

Every environment-dependent value lives here. Override any value with an
environment variable of the same name (for example ``BASE_URL=... pytest``).
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Application URLs -------------------------------------------------------
BASE_URL = os.getenv("BASE_URL", "https://automationexercise.com").rstrip("/")
API_BASE_URL = os.getenv("API_BASE_URL", "https://automationexercise.com").rstrip("/")

UI_PATHS = {
    "home": "/",
    "login": "/login",
    "logout": "/logout",
    "products": "/products",
    "cart": "/view_cart",
    "test_cases": "/test_cases",
    "api_list": "/api_list",
    "delete_account": "/delete_account",
}

# --- Browser settings -------------------------------------------------------
BROWSER = os.getenv("BROWSER", "chromium")                      # chromium | firefox | webkit
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "0"))                        # ms, debugging aid
DEFAULT_TIMEOUT_MS = int(os.getenv("DEFAULT_TIMEOUT_MS", "15000"))
NAVIGATION_TIMEOUT_MS = int(os.getenv("NAVIGATION_TIMEOUT_MS", "30000"))
VIEWPORT = {"width": 1366, "height": 768}

# --- API settings -----------------------------------------------------------
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "30"))

# --- Test data --------------------------------------------------------------
# Known credentials are NOT used for the main flows: every test that needs a
# user creates a disposable one with a unique e-mail and deletes it afterwards.
TEST_EMAIL_DOMAIN = os.getenv("TEST_EMAIL_DOMAIN", "example.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "CapstonePass#2026")
SEARCH_TERM = os.getenv("SEARCH_TERM", "top")                   # documented search keyword used by the API list

# --- Reporting & artifacts --------------------------------------------------
REPORTS_DIR = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
HTML_REPORT_PATH = REPORTS_DIR / "report.html"
