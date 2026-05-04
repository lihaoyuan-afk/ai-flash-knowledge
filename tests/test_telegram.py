from app.models import SourceType
from app.telegram import parse_update


def test_parse_text_update() -> None:
    content = parse_update(
        {
            "message": {
                "message_id": 1,
                "chat": {"id": 100},
                "from": {"id": 200},
                "text": "今天学习 FastAPI",
            }
        }
    )

    assert content is not None
    assert content.chat_id == 100
    assert content.source_type == SourceType.text


def test_parse_link_update() -> None:
    content = parse_update(
        {
            "message": {
                "chat": {"id": 100},
                "from": {"id": 200},
                "text": "https://example.com/article",
            }
        }
    )

    assert content is not None
    assert content.source_type == SourceType.link
    assert content.source_url == "https://example.com/article"


def test_parse_voice_update() -> None:
    content = parse_update(
        {
            "message": {
                "chat": {"id": 100},
                "from": {"id": 200},
                "voice": {"file_id": "abc"},
            }
        }
    )

    assert content is not None
    assert content.source_type == SourceType.audio
    assert content.voice_file_id == "abc"


def test_parse_photo_update_uses_largest_photo() -> None:
    content = parse_update(
        {
            "message": {
                "chat": {"id": 100},
                "from": {"id": 200},
                "caption": "please answer this",
                "photo": [
                    {"file_id": "small", "file_size": 10},
                    {"file_id": "large", "file_size": 100},
                ],
            }
        }
    )

    assert content is not None
    assert content.source_type == SourceType.image_question
    assert content.photo_file_id == "large"
    assert content.text == "please answer this"
