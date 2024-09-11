import pytest
from django.core.cache import cache


@pytest.fixture
def cleared_django_default_cache() -> None:
    cache.clear()


@pytest.fixture
async def acleared_django_default_cache() -> None:
    await cache.aclear()
