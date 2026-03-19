"""Keyword detection and word forms generation service

Generates morphological word forms for keywords (Ukrainian/Russian via pymorphy3,
English via inflect) and searches for them in message text for fast detection.
"""

import json

import inflect
import pymorphy3

from src.config import settings
from src.utils.logger import logger

morph_uk = pymorphy3.MorphAnalyzer(lang="uk")
p_en = inflect.engine()

# ToDo for future: as an improvement use redis/etc or other more advanced caching methods # pylint: disable=fixme


class KeywordService:
    """
    Keyword detection service with morphological word form generation.

    Features:
    - Loads keywords from JSON configuration
    - Generates all possible word forms for comprehensive search
    - Caches word forms in memory for fast lookup
    - Supports Ukrainian, Russian (pymorphy3), and English (inflect) morphology
    - Performs O(n) search in message text for efficiency

    Attributes:
        _cache: Set of all generated keyword forms, or None if not loaded
    """

    def __init__(self) -> None:
        """Initialize keyword service with empty cache."""
        self._cache: set[str] | None = None

    def _load_keyword_forms(self) -> None:
        """
        Load keywords from JSON file and generate all word forms (lazy load).

        Process:
        1. Read keywords from settings.KEYWORDS_FILE
        2. Extract keywords from each category
        3. Generate morphological forms for each keyword
        4. Cache all unique forms in memory

        Expected JSON structure:
            {
                "categories": {
                    "category_name": {
                        "keywords": [
                            {"term": "keyword1"},
                            {"term": "keyword2"}
                        ]
                    }
                }
            }

        Side effects:
            - Populates self._cache with all generated word forms
            - Logs success/error messages via logger
            - Creates empty set if file missing or JSON invalid

        Notes:
            - Only loads once - subsequent calls check if already loaded
            - Uses _get_word_forms() for morphological analysis
        """

        if self._cache is not None:
            return

        try:
            keywords_path = settings.KEYWORDS_FILE
            if not keywords_path.exists():
                logger.error("Keywords file not found: %s", keywords_path)
                self._cache = set()
                return

            with keywords_path.open(encoding="utf-8") as f:
                data = json.load(f)
                keywords = set()
                for category in data.get("categories", {}).values():
                    for item in category.get("keywords", []):
                        term = item.get("term")
                        if term:
                            keywords.add(term.strip())

            if not keywords:
                logger.error("No keywords found in file")
                self._cache = set()
                return

            all_forms = self._get_word_forms(keywords)
            self._cache = all_forms
            logger.success(
                f"Keyword forms generated: {len(all_forms)} unique forms saved to cache"
            )

        except Exception as e:
            logger.critical("Failed to generate keyword forms: %s", e, exc_info=True)
            self._cache = set()

    @staticmethod
    def _get_word_forms(words_list: set[str]) -> set[str]:
        """
        Generate all possible morphological word forms from keywords.

        Handles multiple languages:
        - Ukrainian/Russian: Uses pymorphy3 MorphAnalyzer
        - English: Uses inflect library for pluralization
        - Mixed/Unknown: Adds as-is to forms

        Args:
            words_list: Set of keyword terms to generate forms for

        Returns:
            set[str]: All unique word forms (lowercase) including:
                - Original forms
                - Singular/plural variants
                - Grammatical cases (for Ukrainian/Russian)
        """

        all_forms = set()
        for word in words_list:
            w = word.lower().strip()
            if not w:
                continue
            if any(
                c in "а-щїґєіьюя" for c in w
            ):  # ukrainian/russian words - use pymorphy3
                parses = morph_uk.parse(w)
                for p in parses:
                    for form in p.lexeme:
                        all_forms.add(form.word)
            elif (
                any(c.isalpha() for c in w) and w.isascii()
            ):  # english words - use inflect
                all_forms.add(w)
                plural = p_en.plural(w)
                if plural:
                    all_forms.add(plural)
                singular = p_en.singular_noun(w)
                if singular:
                    all_forms.add(singular)
            else:
                all_forms.add(w)
        return all_forms

    def preload(self) -> None:
        """
        Force preload keyword forms at application startup.

        Ensures all word forms are loaded before message processing begins.
        Called during bootstrap to avoid lazy loading delays during message handling.

        Side effects:
            - Calls _load_keyword_forms() to populate cache
            - Logs any errors that occur
        """

        if self._cache is None:
            self._load_keyword_forms()

    def find_keyword_in_message_text(self, message_text: str) -> tuple[bool, str]:
        """
        Fast keyword search in message text.

        Performs substring search of all cached keyword forms in lowercase message.
        Stops at first match for efficiency.

        Args:
            message_text: Message text to search

        Returns:
            tuple[bool, str]: Tuple containing:
                - bool: True if any keyword form found, False otherwise
                - str: Matched keyword form (or "-" if not found)

        Side effects:
            - Calls _load_keyword_forms() if cache not yet initialized
            - Logs warning if lazy loading occurs
            - Logs error if search fails

        Notes:
            - Performs case-insensitive search
            - Uses substring matching (not word boundaries)
            - Returns first match found
        """

        try:
            if self._cache is None:
                logger.warning("Keyword forms cache not found - generating on the fly")
                self._load_keyword_forms()

            message_lower = message_text.lower()
            for form in self._cache:
                if form in message_lower:
                    return True, form
            return False, "-"
        except Exception as e:
            logger.error("Keyword search failed: %s", e, exc_info=True)
            return False, "-"


get_keywords: KeywordService = KeywordService()
