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


def get_word_forms(words_list: set[str]) -> set[str]:
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

        if any(c in "а-щїґєіьюя" for c in w):  # ukrainian/russian words - use pymorphy3
            parses = morph_uk.parse(w)
            for p in parses:
                for form in p.lexeme:
                    all_forms.add(form.word)
        elif any(c.isalpha() for c in w) and w.isascii():  # english words - use inflect
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


def generate_keyword_forms():
    """Read keywords.json > generate word forms > save in keyword_forms.json"""

    try:
        keywords_path = settings.KEYWORDS_FILE
        if not keywords_path.exists():
            logger.error(f"Keywords file not found: {keywords_path}")
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
            return

        all_forms = get_word_forms(keywords)

        cache_path = settings.KEYWORD_FORMS_CACHE
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(sorted(all_forms), f, ensure_ascii=False, indent=2)
            f.write("\n")

        logger.info(
            f"Keyword forms generated: {len(all_forms)} unique forms saved to {cache_path}"
        )
    except Exception as e:
        logger.critical(f"Failed to generate keyword forms: {e}", exc_info=True)


def find_keyword_in_message_text(message_text: str) -> tuple[bool, str]:
    """
    Fast keyword search in message text.
    Use cached word forms with keyword_forms.json
    Return (True, keyword) or (False, None)
    """

    try:
        cache_path = settings.KEYWORD_FORMS_CACHE
        if not cache_path.exists():
            logger.warning("Keyword forms cache not found - generating on the fly")
            generate_keyword_forms()

        with cache_path.open(encoding="utf-8") as f:
            forms = set(json.load(f))

        message_lower = message_text.lower()
        for form in forms:
            if form in message_lower:
                return True, form

        return False, "-"
    except Exception as e:
        logger.error(f"Keyword search failed: {e}", exc_info=True)
        return False, "-"
