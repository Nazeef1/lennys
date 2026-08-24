import os
import pytest
from backend.app.rag.engine import RAGEngine

def test_rag_chunking_and_indexing(tmp_path):
    # Create sample transcript file
    sample_file = tmp_path / "test_guest.md"
    sample_file.write_text("""---
title: "Test Guest on Growth Loops"
date: "2026-08-01"
guest: "Test Guest"
post_url: "https://lenny.com/test"
---

Product-led growth relies on viral loops and acquisition retention flywheels.

When retention is strong, monetization follows naturally.
""", encoding="utf-8")

    engine = RAGEngine(transcript_dir=str(tmp_path))
    chunk_count = engine.build_index()
    assert chunk_count > 0
    assert engine.is_indexed is True

    # Test search query
    results = engine.search("retention flywheels", top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top.guest == "Test Guest"
    assert "viral loops" in top.content
