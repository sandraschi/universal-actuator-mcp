from unittest.mock import patch

import pytest

from universal_actuator_mcp.rag import LanceDBRag


@pytest.fixture
def temp_rag_db(tmp_path):
    """Fixture for a clean LanceDB instance."""
    db_dir = tmp_path / "lancedb_test"
    db_dir.mkdir()
    return LanceDBRag(db_path=db_dir)


@pytest.mark.asyncio
async def test_rag_initialize(temp_rag_db):
    with patch("sentence_transformers.SentenceTransformer", side_effect=ImportError):
        await temp_rag_db.initialize()
        assert temp_rag_db._initialized is True
        assert temp_rag_db._embed_model_name == "hash-fallback"
        assert temp_rag_db.db_path.exists()


@pytest.mark.asyncio
async def test_rag_ingest_and_search(temp_rag_db):
    await temp_rag_db.initialize()

    items = [
        {
            "id": "1",
            "title": "Plex Movie",
            "author": "2024",
            "source": "plex",
            "type": "movie",
            "metadata": {"summary": "Sci-fi"},
        },
        {
            "id": "2",
            "title": "Calibre Book",
            "author": "Author A",
            "source": "calibre",
            "type": "book",
            "metadata": {"tags": ["AI"]},
        },
    ]

    ingested = await temp_rag_db.ingest_items(items)
    assert ingested == 2

    # Test semantic search
    results = await temp_rag_db.semantic_search("Plex", limit=1)
    assert len(results) == 1
    assert results[0]["title"] == "Plex Movie"
    assert results[0]["source"] == "plex"

    # Test search with filter
    results_filtered = await temp_rag_db.semantic_search("Movie", source_filter="calibre")
    # All items are retrieved and then filtered by source if logic allows,
    # but here it should likely return the calibre book or empty if nothing matches 'Movie' vector near Calibre result.
    # Note: hash-embeddings are deterministic but not very semantic.
    assert all(r["source"] == "calibre" for r in results_filtered)


@pytest.mark.asyncio
async def test_rag_stats(temp_rag_db):
    await temp_rag_db.initialize()
    await temp_rag_db.ingest_items([{"id": "a", "source": "calibre"}])

    stats = await temp_rag_db.stats()
    assert stats["initialized"] is True
    assert stats["total_items"] == 1
    assert "calibre" in stats["source_distribution"]


@pytest.mark.asyncio
async def test_rag_clear(temp_rag_db):
    await temp_rag_db.initialize()
    await temp_rag_db.ingest_items([{"id": "a", "source": "calibre"}])
    assert len(temp_rag_db._table) == 1

    await temp_rag_db.clear()
    assert len(temp_rag_db._table) == 0


@pytest.mark.asyncio
async def test_rag_uninitialized_calls(temp_rag_db):
    # Search on uninitialized should auto-init
    results = await temp_rag_db.semantic_search("test")
    assert temp_rag_db._initialized is True
    assert results == []
