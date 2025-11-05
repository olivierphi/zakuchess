from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from apps.daily_challenge.models import DailyChallenge

if TYPE_CHECKING:
    from django.test import Client as DjangoClient


@pytest.fixture
def fallback_daily_challenge():
    return DailyChallenge.objects.create(
        lookup_key="fallback_1",
        source=None,
        status=1,
        fen="6k1/7p/1Q2P2p/4P3/qb2Nr2/1n3N1P/5PP1/5RK1 w - - 3 27",
        teams={
            "w": [
                {"id": "p1", "type": "p", "name": ["P1", "MacPawny"]},
                {"id": "p2", "type": "p", "name": ["P2", "MacPawny"]},
                {"id": "p3", "type": "p", "name": ["P3", "MacPawny"]},
                {"id": "p4", "type": "p", "name": ["P4", "MacPawny"]},
                {"id": "p5", "type": "p", "name": ["P5", "MacPawny"]},
                {"id": "n1", "type": "n", "name": ["N1", "MacKnighty"]},
                {"id": "n2", "type": "n", "name": ["N2", "MacKnighty"]},
                {"id": "r1", "type": "r", "name": ["R1", "MacRookie"]},
                {"id": "q", "type": "q", "name": ["Q", "MacQueeny"]},
                {"id": "k", "type": "k", "name": ["K", "MacKingy"]},
            ],
            "b": [
                {"id": "p1", "type": "p"},
                {"id": "p2", "type": "p"},
                {"id": "n1", "type": "n"},
                {"id": "b1", "type": "b"},
                {"id": "r1", "type": "r"},
                {"id": "q", "type": "q"},
                {"id": "k", "type": "k"},
            ],
        },
        character_id_by_square={
            "g8": "k",
            "h7": "p1",
            "h6": "p2",
            "e6": "p1",
            "b6": "q",
            "e5": "p2",
            "f4": "r1",
            "e4": "n1",
            "b4": "b1",
            "a4": "q",
            "h3": "p3",
            "f3": "n2",
            "b3": "n1",
            "g2": "p4",
            "f2": "p5",
            "g1": "k",
            "f1": "r1",
        },
        bot_first_move="f8f4",
        bot_depth=1,
        player_simulated_depth=5,
        intro_turn_speech_square="e4",
        starting_advantage=10,
        solution="e4f6,f4f6,e5f6,b3d2,f6f7,g8g7,b6d4,g7g6,f3h4,g6g5,d4e5,g5h4,e5g3,h4h5,g3g4",
        intro_turn_speech_text="",
    )


@pytest.mark.django_db
def test_homepage_smoke_test(client: DjangoClient, fallback_daily_challenge):
    response = client.get("/")
    assert response.status_code == 200
