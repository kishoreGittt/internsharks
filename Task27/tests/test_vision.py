def test_invalid_image(
    authenticated_client
):

    response = authenticated_client.post(

        "/ai/vision",

        files={
            "image": (
                "test.txt",
                b"hello",
                "text/plain"
            )
        },

        data={
            "prompt":
                "What is this?"
        }
    )

    assert response.status_code == 400