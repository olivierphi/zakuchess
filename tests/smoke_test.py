from django.test import Client


def test_alive(client: Client):
    resp = client.get("/-/alive/")
    assert resp.status_code == 200
    assert resp.content == b"ok"
