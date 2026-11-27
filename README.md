# Automation Exercise – E2E & API Test Automation (Capstone)

Python test automation framework for [automationexercise.com](https://automationexercise.com/) covering:

- **UI tests** with Playwright (Python) using the Page Object Model
- **REST API tests** for the documented endpoints in the [API list](https://automationexercise.com/api_list)
- **Negative tests** for both UI and API
- **Pytest HTML and JUnit reports** with screenshots on UI failures
- **GitHub Actions** workflow that runs the suite and uploads reports as artifacts

## Project structure

```
capstone-project/
├── .github/workflows/tests.yml   # CI pipeline (runs tests, uploads reports)
├── config/settings.py            # Centralised configuration (env-overridable)
├── pages/                        # Page Object Model
│   ├── base_page.py              #   shared navigation & helpers
│   ├── home_page.py              #   home page + subscription
│   ├── auth_pages.py             #   login/signup, account form, confirmations
│   ├── product_pages.py          #   products, search, categories, brands, details, cart
│   └── account_pages.py          #   logout / delete account
├── tests/
│   ├── ui/                       # UI scenarios 1–15 (+ supporting checks)
│   │   ├── test_auth.py
│   │   └── test_home_and_navigation.py
│   └── api/                      # API scenarios 1–8 + negative scenarios
│       ├── test_products_and_brands_api.py
│       ├── test_account_api.py
│       └── test_unsupported_methods_api.py
├── utils/
│   ├── api_client.py             # requests-based API client with response wrapper
│   └── data_factory.py           # unique, disposable test data
├── conftest.py                   # fixtures, browser lifecycle, failure screenshots
├── pytest.ini                    # markers and report options
└── requirements.txt
```

## Prerequisites

- Python 3.10+ (tested with 3.13)
- pip
- Git (to clone)

## Installation

```bash
git clone <your-repo-url>
cd capstone-project
python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# macOS / Linux:         source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Running the tests

```bash
# Everything (UI + API) – HTML report is written to reports/report.html
pytest

# UI only / API only
pytest -m ui
pytest -m api

# A single file or test
pytest tests/api/test_account_api.py
pytest tests/ui/test_auth.py::test_logout

# Run the UI in a visible browser, slowed down for debugging
HEADLESS=false SLOW_MO=500 pytest -m ui
```

On Windows PowerShell, set environment variables with `$env:HEADLESS="false"` before the command.

### Configuration

All settings are in [config/settings.py](config/settings.py) and can be overridden with environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `BASE_URL` | `https://automationexercise.com` | UI base URL |
| `API_BASE_URL` | `https://automationexercise.com` | API base URL |
| `BROWSER` | `chromium` | `chromium`, `firefox` or `webkit` |
| `HEADLESS` | `true` | Run browser without a window |
| `SLOW_MO` | `0` | Delay (ms) between browser actions |
| `TEST_PASSWORD` | `CapstonePass#2026` | Password for disposable test accounts |
| `SEARCH_TERM` | `top` | Search keyword used by the API search test |

## Reports and evidence

After every run:

- `reports/report.html` – self-contained Pytest HTML report (open in a browser)
- `reports/junit.xml` – JUnit XML for CI integration
- `reports/screenshots/<test_name>.png` – full-page screenshot for each failed UI test (the path is also listed under the failed test in the HTML report)

In GitHub Actions the whole `reports/` folder is uploaded as the **test-reports** artifact.

## Test data rules

- Every account is **disposable**: created with a unique e-mail (`capstone_<random>@example.com`), used, and deleted again (fixtures delete it even when a test fails).
- No real personal data or payment details are used. Address and phone values are synthetic.
- Tests never rely on accounts created by other people.
- The site is a shared public practice environment. If an endpoint or page behaves differently from its documentation, the test fails and the **actual** response is in the failure message. Failures are not hidden.

## CI – GitHub Actions

The workflow `.github/workflows/tests.yml`:

**Runner requirement:** it runs on a *self-hosted* runner with the label `capstone`, not on GitHub-hosted runners. The shared site serves a "Please wait while your request is being verified..." page to GitHub's runners, which blocks the tests. To register one: **Settings → Actions → Runners → New self-hosted runner** (Windows), then run the `config` command with the label `capstone` and start `run`.

1. runs on pushes to `main` and `capstone/**` branches, and can be started manually. It does not run on pull requests, to keep other people's code off the self-hosted runner;
2. installs dependencies and the Playwright Chromium browser;
3. runs the API tests (`pytest -m api`), then the UI tests (`pytest -m ui`) with one automatic rerun per failing test (`pytest-rerunfailures`);
4. uploads `reports/` as the `test-reports` artifact (kept for 14 days). It contains `api-report.html`, `ui-report.html`, `api-results.xml` and `ui-results.xml`;
5. the job fails if any test step fails.

## Scenario coverage

| # | UI scenario | Test |
|---|---|---|
| 1 | Home page loads | `tests/ui/test_home_and_navigation.py::test_home_page_loads_successfully` |
| 2 | Register new user | `tests/ui/test_auth.py::test_register_new_user` |
| 3 | Account creation verified | `test_register_new_user` (ACCOUNT CREATED! + logged-in state) |
| 4 | Login with valid credentials | `tests/ui/test_auth.py::test_login_with_valid_credentials` |
| 5 | Login with invalid credentials | `tests/ui/test_auth.py::test_login_with_invalid_credentials` (3 cases) |
| 6 | Logout | `tests/ui/test_auth.py::test_logout` |
| 7 | Navigate to Products | `test_navigate_to_products_page` |
| 8 | Search and verify results | `test_search_product_returns_matching_results`, `test_search_with_no_match_shows_no_products` |
| 9 | View product details | `test_view_product_details`, `test_view_product_details_from_listing` |
| 10 | Add product to cart | `test_add_product_to_cart_from_details_page` |
| 11 | Verify product and quantity in cart | `test_cart_shows_correct_product_and_quantity` (quantities 1 and 4) |
| 12 | Remove product from cart | `test_remove_product_from_cart` |
| 13 | Product categories | `test_navigate_product_categories` (2 cases) |
| 14 | Product brands | `test_navigate_product_brands` (2 cases) |
| 15 | Subscription | `test_subscribe_to_newsletter` |

| # | API scenario | Method & endpoint | Test |
|---|---|---|---|
| 1 | Get all products | `GET /api/productsList` | `test_products_and_brands_api.py::test_get_all_products_list` |
| 2 | Get all brands | `GET /api/brandsList` | `test_products_and_brands_api.py::test_get_all_brands_list` |
| 3 | Search products | `POST /api/searchProduct` | `test_search_product_returns_matches`, `test_search_product_multiple_terms` |
| 4 | Verify login | `POST /api/verifyLogin` | `test_account_api.py::test_verify_login_with_valid_credentials` |
| 5 | Create user account | `POST /api/createAccount` | `test_account_api.py::test_create_user_account` |
| 6 | Update user account | `PUT /api/updateAccount` | `test_account_api.py::test_update_user_account` |
| 7 | Delete user account | `DELETE /api/deleteAccount` | `test_account_api.py::test_delete_user_account` |
| 8 | Get user details by email | `GET /api/getUserDetailByEmail` | `test_account_api.py::test_get_user_details_by_email` |

Negative API scenarios: search without `search_product` (`test_search_product_without_parameter_returns_400`), invalid login (`test_verify_login_with_invalid_credentials`), login missing email/password (`test_verify_login_without_required_fields`), and documented unsupported methods (`test_unsupported_methods_api.py`).

## Design notes

- **POM**: locators live only in `pages/`; tests describe behaviour and call page methods.
- **Fixtures**: `page`/`context`/`browser` manage Playwright lifecycle; `api` is a shared client; `disposable_user` creates and deletes an account per test.
- **Parametrisation**: used for invalid-login combinations, search terms, categories, brands, cart quantities and invalid login fields.
- **Assertions**: API tests assert both the HTTP status line and the `responseCode` embedded in the body, because this API reports most results in the body.
