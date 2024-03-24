import pytest
from django.core.cache import cache


@pytest.fixture
def cleared_django_default_cache() -> None:
    cache.clear()
