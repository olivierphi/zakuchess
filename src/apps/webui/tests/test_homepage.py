from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.test import Client as DjangoClient


def test_homepage_smoke_test(client: DjangoClient):
    response = client.get("/")
    assert response.status_code == 200
