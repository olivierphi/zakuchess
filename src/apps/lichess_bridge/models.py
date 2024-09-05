from typing import TypeAlias

LichessAccessToken: TypeAlias = str

# >  By convention tokens have a recognizable prefix, but do not rely on this.
# Let's still rely on this for now ^^
# TODO: remove this, as it may break one day?
LICHESS_ACCESS_TOKEN_PREFIX = "lio_"
