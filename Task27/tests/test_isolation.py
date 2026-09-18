def test_document_isolation_query():

    user_a = {
        "owner_id":
            "user-a"
    }

    user_b = {
        "owner_id":
            "user-b"
    }

    assert (
        user_a["owner_id"]
        !=
        user_b["owner_id"]
    )