from typing import TypeAlias

from django.db import models

LichessAccessToken: TypeAlias = str  # e.g. "lio_6EeGimHMalSVH9qMcfUc2JJ3xdBPlqrL"
LichessGameSeekId: TypeAlias = str  # e.g. "oIsGhJaf"

# > By convention tokens have a recognizable prefix, but do not rely on this.
# Well... Let's still rely on this for now ^^
# TODO: remove this, as it may break one day?
LICHESS_ACCESS_TOKEN_PREFIX = "lio_"


class LichessCorrespondenceGameDaysChoice(models.IntegerChoices):
    # https://lichess.org/api#tag/Board/operation/apiBoardSeek
    ONE_DAY = (1, "1 days")
    TWO_DAYS = (2, "2 days")
    THREE_DAYS = (3, "3 days")
    FIVE_DAYS = (5, "5 days")
    SEVEN_DAYS = (7, "7 days")
    TEN_DAYS = (10, "10 days")
    FOURTEEN_DAYS = (14, "14 days")
