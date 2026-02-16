from autofixer_agent.rag.chunking import chunk_text


def test_chunk_text_overlap():
    text = "a" * 2500
    chunks = chunk_text(text, chunk_size=1000, overlap=100)
    assert len(chunks) == 3
    assert len(chunks[0]) == 1000
    assert chunks[0][-100:] == chunks[1][:100]
