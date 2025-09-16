from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.test import Client as DjangoClient


def test_smoke(client: DjangoClient):
    """
    Smoke test to check that we get a successful HTTP response when we query '/-/alive/'.
    """
    response = client.get("/-/alive/")
    assert response.status_code == 200
