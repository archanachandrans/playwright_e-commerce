"""Thin HTTP client for the Automation Exercise REST API.

The API reports its own result in a JSON body field called ``responseCode``
as well as in the HTTP status line. Both are exposed on ``ApiResponse`` so
tests can assert on either one.
"""

from dataclasses import dataclass
from typing import Any

import requests

from config import settings


@dataclass
class ApiResponse:
    status_code: int
    raw_text: str
    body: Any

    @property
    def response_code(self) -> int | None:
        """The ``responseCode`` value embedded in the JSON body, if present."""
        if isinstance(self.body, dict):
            return self.body.get("responseCode")
        return None

    @property
    def message(self) -> str | None:
        if isinstance(self.body, dict):
            return self.body.get("message")
        return None


class ApiClient:
    def __init__(self, base_url: str = settings.API_BASE_URL, timeout: int = settings.API_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _request(self, method: str, path: str, **kwargs) -> ApiResponse:
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        try:
            body = response.json()
        except ValueError:
            body = None
        return ApiResponse(status_code=response.status_code, raw_text=response.text, body=body)

    def get(self, path: str, **kwargs) -> ApiResponse:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> ApiResponse:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> ApiResponse:
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> ApiResponse:
        return self._request("DELETE", path, **kwargs)

    # ----- documented endpoints ----------------------------------------------
    def get_products(self) -> ApiResponse:
        return self.get("/api/productsList")

    def get_brands(self) -> ApiResponse:
        return self.get("/api/brandsList")

    def search_product(self, search_product: str | None = None, **kwargs) -> ApiResponse:
        data = {} if search_product is None else {"search_product": search_product}
        return self.post("/api/searchProduct", data=data, **kwargs)

    def verify_login(self, email: str | None = None, password: str | None = None) -> ApiResponse:
        data = {}
        if email is not None:
            data["email"] = email
        if password is not None:
            data["password"] = password
        return self.post("/api/verifyLogin", data=data)

    def create_account(self, payload: dict) -> ApiResponse:
        return self.post("/api/createAccount", data=payload)

    def update_account(self, payload: dict) -> ApiResponse:
        return self.put("/api/updateAccount", data=payload)

    def delete_account(self, email: str, password: str) -> ApiResponse:
        return self.delete("/api/deleteAccount", data={"email": email, "password": password})

    def get_user_detail_by_email(self, email: str) -> ApiResponse:
        return self.get("/api/getUserDetailByEmail", params={"email": email})
