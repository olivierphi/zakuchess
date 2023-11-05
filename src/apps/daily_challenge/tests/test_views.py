from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from django.test import Client as DjangoClient


@pytest.mark.parametrize(
    ("input_", "expected_status_code"),
    (
        ({"square": "a9"}, HTTPStatus.BAD_REQUEST),
        ({"square": "nope"}, HTTPStatus.BAD_REQUEST),
        ({"square": "f1"}, HTTPStatus.OK),
    ),
)
@pytest.mark.django_db
def test_htmx_game_select_piece_input_validation(
    client: "DjangoClient", input_: dict, expected_status_code: int
):
    client.get("/")
    response = client.get("/htmx/pieces/select/", data=input_)
    assert response.status_code == expected_status_code
