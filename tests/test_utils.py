import pytest

from app.utils import clean_tags, extract_json_object, first_url


def test_first_url_detects_http_url() -> None:
    assert first_url("看看 https://example.com/a?b=1 这篇") == "https://example.com/a?b=1"


def test_extract_json_object_from_fenced_response() -> None:
    data = extract_json_object('```json\n{"title":"标题","summary":"摘要","tags":["开发"]}\n```')
    assert data["title"] == "标题"


def test_extract_json_object_raises_for_invalid_text() -> None:
    with pytest.raises(ValueError):
        extract_json_object("没有 JSON")


def test_clean_tags_limits_and_defaults() -> None:
    assert clean_tags(["效率", "效率", "开发", "生活", "额外"]) == ["效率", "开发", "生活"]
    assert clean_tags([]) == ["未分类"]
