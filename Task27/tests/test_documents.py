def test_invalid_document_type(
    authenticated_client
):

    response = authenticated_client.post(

        "/knowledge/documents",

        files={
            "file": (
                "test.exe",
                b"bad file",
                "application/octet-stream"
            )
        }
    )

    assert response.status_code == 400