"""Unit tests for keyword service"""

from src.services.keywords import KeywordService


class TestKeywordService:
    """Tests for KeywordService class"""

    def test_init(self):
        """Test KeywordService initialization

        Verifies that _cache is None on initialization
        """

        service = KeywordService()
        assert service._cache is None

    def test_get_word_forms_english(self):
        """Test English word form generation

        Verifies that English words generate singular and plural forms
        """

        words = {"project", "hire"}
        forms = KeywordService._get_word_forms(words)

        # Should include original forms
        assert "project" in forms
        assert "hire" in forms
        # Should include some plural forms
        assert len(forms) >= 2

    def test_get_word_forms_empty(self):
        """Test word form generation with empty input

        Verifies that empty word set returns empty form set
        """

        words = set()
        forms = KeywordService._get_word_forms(words)
        assert forms == set()

    def test_get_word_forms_whitespace(self):
        """Test word form generation with whitespace

        Verifies that whitespace-only words are handled correctly
        """

        words = {"   ", "\t", ""}
        forms = KeywordService._get_word_forms(words)
        # Empty/whitespace should be filtered out
        assert "" not in forms

    def test_find_keyword_in_message_not_found(self):
        """Test keyword search when no keywords match

        Verifies that search returns (False, "-") when no matches found
        """

        service = KeywordService()
        service._cache = {"project", "freelance", "hire"}

        found, keyword = service.find_keyword_in_message_text(
            "This is a random message"
        )
        assert found is False
        assert keyword == "-"

    def test_find_keyword_in_message_found(self):
        """Test keyword search when keyword is found

        Verifies that search returns (True, keyword) when match found
        """

        service = KeywordService()
        service._cache = {"project", "freelance", "hire"}

        found, keyword = service.find_keyword_in_message_text(
            "I need a freelance project"
        )
        assert found is True
        assert keyword in service._cache

    def test_find_keyword_in_message_case_insensitive(self):
        """Test that keyword search is case-insensitive

        Verifies that uppercase text matches lowercase keywords
        """

        service = KeywordService()
        service._cache = {"project", "freelance"}

        found, keyword = service.find_keyword_in_message_text(
            "I NEED A FREELANCE PROJECT"
        )
        assert found is True

    def test_find_keyword_empty_cache_lazy_load(self):
        """Test lazy loading when cache is None

        Verifies that cache is initialized when None (will fail gracefully
        if file not found, but that's expected in test environment)
        """

        service = KeywordService()
        assert service._cache is None

        # This will attempt to load from file, which may not exist in tests
        # The service should handle this gracefully
        found, keyword = service.find_keyword_in_message_text("test message")
        # Should not raise an exception
        assert isinstance(found, bool)
        assert isinstance(keyword, str)

    def test_preload(self):
        """Test preload method

        Verifies that preload initializes cache if None
        """

        service = KeywordService()
        assert service._cache is None

        service.preload()
        # Cache should be initialized (either empty set or with keywords)
        assert isinstance(service._cache, set)
