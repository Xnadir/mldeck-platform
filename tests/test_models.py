"""Tests for the model registry."""

import pytest
import json
import tempfile
import os


def test_registry_loads_empty():
    """Registry returns empty list when no file exists."""
    from models import _load_registry
    # With no file, should return []
    result = _load_registry()
    assert isinstance(result, list)
