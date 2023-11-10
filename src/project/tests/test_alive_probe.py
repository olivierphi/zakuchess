from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.test import Client as DjangoClient


def test_alive(client: "DjangoClient"):
    resp = client.get("/-/alive/")
    assert resp.status_code == 200
    assert resp.content == b"ok"
