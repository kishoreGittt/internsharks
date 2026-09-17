
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.models.vision import VisionResult


client = TestClient(app)


def create_image(
    image_format: str = "PNG",
    color: str = "red",
) -> bytes:

    image = Image.new(
        "RGB",
        (100, 100),
        color=color,
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format=image_format,
    )

    return buffer.getvalue()


def fake_vision_result():
    return VisionResult(
        analysis_type="general",
        description="A red object is visible.",
        visible_text=[],
        objects=["object"],
        attributes={"color": "red"},
        uncertain_details=[],
        observed=["A red object is visible."],
        not_determinable=[],
    )


@pytest.mark.parametrize(
    "image_format,content_type",
    [
        ("PNG", "image/png"),
        ("JPEG", "image/jpeg"),
        ("WEBP", "image/webp"),
    ],
)
def test_valid_image(
    monkeypatch,
    image_format,
    content_type,
):

    async def fake_call(*args, **kwargs):
        return fake_vision_result()

    monkeypatch.setattr(
        "app.routes.vision.call_vision_model",
        fake_call,
    )

    response = client.post(
        "/ai/vision/analyze",
        files={
            "image": (
                f"test.{image_format.lower()}",
                create_image(image_format),
                content_type,
            )
        },
        data={
            "prompt": "Describe this image.",
            "analysis_type": "general",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_empty_image():

    response = client.post(
        "/ai/vision/analyze",
        files={
            "image": (
                "empty.png",
                b"",
                "image/png",
            )
        },
        data={
            "prompt": "Describe this image.",
            "analysis_type": "general",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "EMPTY_IMAGE"


def test_corrupted_image():

    response = client.post(
        "/ai/vision/analyze",
        files={
            "image": (
                "corrupted.png",
                b"this is not a real image",
                "image/png",
            )
        },
        data={
            "prompt": "Describe this image.",
            "analysis_type": "general",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "INVALID_IMAGE"


def test_unsupported_file_type():

    response = client.post(
        "/ai/vision/analyze",
        files={
            "image": (
                "test.txt",
                b"hello",
                "text/plain",
            )
        },
        data={
            "prompt": "Describe this image.",
            "analysis_type": "general",
        },
    )

    assert response.status_code == 415
    assert (
        response.json()["detail"]["error"]
        == "UNSUPPORTED_IMAGE_TYPE"
    )


def test_missing_prompt():

    response = client.post(
        "/ai/vision/analyze",
        files={
            "image": (
                "test.png",
                create_image(),
                "image/png",
            )
        },
        data={
            "analysis_type": "general",
        },
    )

    assert response.status_code == 422


def test_empty_prompt():

    response = client.post(
        "/ai/vision/analyze",
        files={
            "image": (
                "test.png",
                create_image(),
                "image/png",
            )
        },
        data={
            "prompt": "   ",
            "analysis_type": "general",
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["error"]
        == "EMPTY_PROMPT"
    )


def test_invalid_analysis_type():

    response = client.post(
        "/ai/vision/analyze",
        files={
            "image": (
                "test.png",
                create_image(),
                "image/png",
            )
        },
        data={
            "prompt": "Describe this image.",
            "analysis_type": "invalid",
        },
    )

    assert response.status_code == 422


def test_root():

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_health():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"