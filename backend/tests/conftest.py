from __future__ import annotations

import pytest

from app.services.catalog import AnimeCatalog


@pytest.fixture(scope="session")
def catalog() -> AnimeCatalog:
    return AnimeCatalog()
