import pytest


@pytest.fixture
def sample_text():
    """Sample text for testing chunking."""
    return """
    This is a sample document for testing. It contains multiple sentences.
    The quick brown fox jumps over the lazy dog. This is another sentence.
    We need enough text to test the chunking functionality properly.
    The chunking algorithm should split this into multiple chunks with overlap.
    """
