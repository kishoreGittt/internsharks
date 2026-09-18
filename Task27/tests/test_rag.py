from app.services.rag_service import (
    build_context
)


def test_empty_rag_context():

    result = build_context(
        []
    )

    assert result == ""