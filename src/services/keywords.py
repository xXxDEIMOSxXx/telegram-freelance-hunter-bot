"""
Service that generates keyword forms (for wider search range)
and find this keywords in telegram messages
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
    """Keyword service class"""

    def __init__(self):
        self._cache: set[str] | None = None

    def _load_keyword_forms(self) -> None:
        """Load keywords from file > generate word forms → save in cache (one time)"""

        if self._cache is not None:
            return

        try:
            keywords_path = settings.KEYWORDS_FILE
            if not keywords_path.exists():
                logger.error(f"Keywords file not found: {keywords_path}")
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
            logger.critical(f"Failed to generate keyword forms: {e}", exc_info=True)
            self._cache = set()

    @staticmethod
    def _get_word_forms(words_list: set[str]) -> set[str]:
        """
        Generates all possible word forms from keywords.json
        (Ukrainian/russian via pymorphy3, English via inflect).
        Returns a set of unique forms.
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
        """Force generate keyword forms at startup"""

        if self._cache is None:
            self._load_keyword_forms()

    def find_keyword_in_message_text(self, message_text: str) -> tuple[bool, str]:
        """Fast keyword search in message text"""

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
            logger.error(f"Keyword search failed: {e}", exc_info=True)
            return False, "-"


get_keywords = KeywordService()
