import pytest
from services.ai_service import ai_service


class TestAIServiceJSONParsing:
    """AI service'ning JSON parsing qobiliyatini tekshirish"""

    def test_parse_clean_json(self):
        raw = '{"title": "Test", "subject": "Info"}'
        result = ai_service._extract_and_parse_json(raw, {})
        assert result["title"] == "Test"

    def test_parse_json_with_markdown_fence(self):
        raw = '```json\n{"title": "AI Test"}\n```'
        result = ai_service._extract_and_parse_json(raw, {})
        assert result["title"] == "AI Test"

    def test_parse_json_with_surrounding_text(self):
        raw = 'Here is the result:\n{"title": "Embedded"}\nDone.'
        result = ai_service._extract_and_parse_json(raw, {})
        assert result["title"] == "Embedded"

    def test_parse_invalid_json_returns_default(self):
        raw = 'This is not JSON at all'
        default = {"title": "Default"}
        result = ai_service._extract_and_parse_json(raw, default)
        assert result["title"] == "Default"

    def test_parse_empty_string_returns_default(self):
        result = ai_service._extract_and_parse_json("", {"fallback": True})
        assert result["fallback"] is True

    def test_parse_json_array(self):
        raw = '[{"q": "Test?"}]'
        result = ai_service._extract_and_parse_json(raw, [])
        assert isinstance(result, list)
        assert result[0]["q"] == "Test?"

    def test_parse_json_with_language_tag(self):
        raw = '```json\n{"key": "value"}\n```'
        result = ai_service._extract_and_parse_json(raw, {})
        assert result["key"] == "value"

    def test_parse_nested_json(self):
        raw = '{"chapters": [{"title": "Bob 1", "sections": [{"subtitle": "1.1", "text": "Matn"}]}]}'
        result = ai_service._extract_and_parse_json(raw, {})
        assert len(result["chapters"]) == 1
        assert result["chapters"][0]["sections"][0]["subtitle"] == "1.1"
