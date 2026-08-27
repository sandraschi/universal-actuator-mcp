"""
LanceDB-based RAG engine for Universal Actuator MCP.

Provides semantic vector search over federated media metadata (Calibre, Plex, Immich).
Uses sentence-transformers (all-MiniLM-L6-v2) when available; falls back to
deterministic hash-embeddings so the index still functions for FTS-style proximity.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("univact.rag")

# Embedding dimension for all-MiniLM-L6-v2 (and the hash fallback)
EMBED_DIM = 384
# Point to the existing state directory in the root
RAG_DB_PATH = Path(__file__).parent.parent.parent / "backend" / "state" / "lancedb"


class LanceDBRag:
    """
    Vector RAG engine backed by LanceDB.

    Lifecycle:
        rag = LanceDBRag()
        await rag.initialize()          # call once at server startup (lifespan)
        await rag.ingest_items(items)   # add media items
        results = await rag.semantic_search("sci-fi 2001")
    """

    def __init__(self, db_path: Path = RAG_DB_PATH) -> None:
        self.db_path = db_path
        self._db: Any = None
        self._table: Any = None
        self._embedder: Any = None
        self._initialized: bool = False
        self._embed_model_name: str = "hash-fallback"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _hash_embed(self, text: str) -> list[float]:
        """Deterministic pseudo-embedding from MD5 - fallback when no model loaded."""
        # MD5 is used here for deterministic pseudo-embeddings, not for security.
        seed = int(hashlib.md5(text.lower().encode()).hexdigest(), 16)
        vec: list[float] = []
        for i in range(EMBED_DIM):
            val = float((seed >> (i % 64)) & 0xFF) - 127.5
            vec.append(val)
        norm = (sum(v * v for v in vec) ** 0.5) or 1.0
        return [v / norm for v in vec]

    def _embed(self, text: str) -> list[float]:
        """Embed text synchronously (called in executor for async safety)."""
        if self._embedder is not None:
            return self._embedder.encode(text, convert_to_numpy=True).tolist()
        return self._hash_embed(text)

    async def _async_embed(self, text: str) -> list[float]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._embed, text)

    def _make_schema(self) -> Any:
        import pyarrow as pa

        return pa.schema(
            [
                pa.field("id", pa.string()),
                pa.field("title", pa.string()),
                pa.field("author", pa.string()),
                pa.field("source", pa.string()),
                pa.field("item_type", pa.string()),
                pa.field("metadata_json", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), EMBED_DIM)),
            ]
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """
        Initialize LanceDB connection, optionally load sentence-transformers,
        and open (or create) the media_items table.
        """
        import lancedb

        self.db_path.mkdir(parents=True, exist_ok=True)
        self._db = lancedb.connect(str(self.db_path))

        # Try sentence-transformers; fail gracefully
        try:
            from sentence_transformers import SentenceTransformer

            loop = asyncio.get_event_loop()
            self._embedder = await loop.run_in_executor(None, SentenceTransformer, "all-MiniLM-L6-v2")
            self._embed_model_name = "all-MiniLM-L6-v2"
            logger.info("RAG: SentenceTransformer loaded (384-dim vectors).")
        except ImportError:
            logger.warning(
                "RAG: sentence-transformers not installed - using hash embeddings. "
                "Install with: pip install sentence-transformers"
            )

        # Open or create table
        if "media_items" in self._db.table_names():
            self._table = self._db.open_table("media_items")
            logger.info(f"RAG: Opened existing table 'media_items' ({len(self._table)} rows).")
        else:
            self._table = self._db.create_table("media_items", schema=self._make_schema())
            logger.info("RAG: Created new table 'media_items'.")

        self._initialized = True

    async def ingest_items(self, items: list[dict[str, Any]]) -> int:
        """
        Embed and ingest media items into the vector index.

        Each item must contain: id, title, author, source, type.
        Optional: metadata (dict).

        Returns the count of successfully ingested rows.
        """
        if not self._initialized:
            await self.initialize()

        rows = []
        for item in items:
            text = " ".join(
                filter(
                    None,
                    [
                        item.get("title", ""),
                        item.get("author", ""),
                        item.get("source", ""),
                        item.get("type", ""),
                    ],
                )
            )
            vector = await self._async_embed(text)
            rows.append(
                {
                    "id": str(item.get("id", "")),
                    "title": str(item.get("title", "")),
                    "author": str(item.get("author", "") or ""),
                    "source": str(item.get("source", "")),
                    "item_type": str(item.get("type", "")),
                    "metadata_json": json.dumps(item.get("metadata", {})),
                    "vector": vector,
                }
            )

        if rows:
            self._table.add(rows)
            logger.info(f"RAG: Ingested {len(rows)} items.")

        return len(rows)

    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        source_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Vector similarity search over the media index.

        Args:
            query: Natural language search query.
            limit: Max results to return.
            source_filter: Restrict to "calibre", "plex", or "immich".

        Returns:
            List of ranked media items with _score (distance, lower = closer).
        """
        if not self._initialized:
            await self.initialize()

        if len(self._table) == 0:
            return []

        query_vec = await self._async_embed(query)

        search = self._table.search(query_vec).limit(limit * 2)
        if source_filter:
            search = search.where(f"source = '{source_filter}'")

        raw = search.to_list()

        results = []
        for row in raw[:limit]:
            try:
                metadata = json.loads(row.get("metadata_json", "{}"))
            except (json.JSONDecodeError, TypeError):
                metadata = {}
            results.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "author": row["author"],
                    "source": row["source"],
                    "type": row["item_type"],
                    "metadata": metadata,
                    "_score": float(row.get("_distance", 0.0)),
                }
            )

        return results

    async def stats(self) -> dict[str, Any]:
        """Return index statistics."""
        if not self._initialized:
            return {"initialized": False, "total_items": 0, "embedding_model": "none"}

        row_count = len(self._table)
        source_counts: dict[str, int] = {}
        if row_count > 0:
            for row in self._table.to_arrow().to_pydict().get("source", []):
                source_counts[row] = source_counts.get(row, 0) + 1

        return {
            "initialized": True,
            "total_items": row_count,
            "embedding_model": self._embed_model_name,
            "db_path": str(self.db_path),
            "source_distribution": source_counts,
        }

    async def clear(self) -> None:
        """Drop and recreate the table (clears all indexed items)."""
        if self._db is not None and self._table is not None:
            self._db.drop_table("media_items")
            self._table = self._db.create_table("media_items", schema=self._make_schema())
            logger.info("RAG: Table cleared and recreated.")
