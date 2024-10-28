# language_utils.py
from typing import Dict, List, Optional


class LanguageUtils:
    # Top 25 languages by number of speakers, mapped to NLLB codes
    LANGUAGE_MAPPING: Dict[str, str] = {
        # Common 2-letter codes to NLLB codes
        "en": "eng_Latn",  # English
        "zh": "zho_Hans",  # Chinese (Simplified)
        "hi": "hin_Deva",  # Hindi
        "es": "spa_Latn",  # Spanish
        "ar": "arb_Arab",  # Arabic
        "ara": "arb_Arab",  # Arabic (3-letter code)
        "bn": "ben_Beng",  # Bengali
        "pt": "por_Latn",  # Portuguese
        "ru": "rus_Cyrl",  # Russian
        "ja": "jpn_Jpan",  # Japanese
        "pa": "pan_Guru",  # Punjabi
        "de": "deu_Latn",  # German
        "jv": "jav_Latn",  # Javanese
        "ko": "kor_Hang",  # Korean
        "fr": "fra_Latn",  # French
        "te": "tel_Telu",  # Telugu
        "mr": "mar_Deva",  # Marathi
        "tr": "tur_Latn",  # Turkish
        "ta": "tam_Taml",  # Tamil
        "vi": "vie_Latn",  # Vietnamese
        "ur": "urd_Arab",  # Urdu
        "id": "ind_Latn",  # Indonesian
        "it": "ita_Latn",  # Italian
        "th": "tha_Thai",  # Thai
        "gu": "guj_Gujr",  # Gujarati
        "pl": "pol_Latn",  # Polish
        # Common variations and full names
        "eng": "eng_Latn",
        "english": "eng_Latn",
        "chinese": "zho_Hans",
        "hindi": "hin_Deva",
        "spanish": "spa_Latn",
        "arabic": "arb_Arab",
        "bengali": "ben_Beng",
        "portuguese": "por_Latn",
        "russian": "rus_Cyrl",
        "japanese": "jpn_Jpan",
        "punjabi": "pan_Guru",
        "german": "deu_Latn",
        "javanese": "jav_Latn",
        "korean": "kor_Hang",
        "french": "fra_Latn",
        "telugu": "tel_Telu",
        "marathi": "mar_Deva",
        "turkish": "tur_Latn",
        "tamil": "tam_Taml",
        "vietnamese": "vie_Latn",
        "urdu": "urd_Arab",
        "indonesian": "ind_Latn",
        "italian": "ita_Latn",
        "thai": "tha_Thai",
        "gujarati": "guj_Gujr",
        "polish": "pol_Latn",
    }

    @classmethod
    def get_nllb_language_code(cls, language_code: str) -> Optional[str]:
        """
        Convert a common language code or name to NLLB-specific language code.
        Returns None if no valid mapping is found.

        Args:
            language_code: A string representing language code (e.g., 'en', 'eng', 'english')

        Returns:
            An NLLB-specific language code or None if not found
        """
        # Convert to lowercase for case-insensitive matching
        language_code = language_code.lower().strip()

        # Direct lookup
        if language_code in cls.LANGUAGE_MAPPING:
            return cls.LANGUAGE_MAPPING[language_code]

        return None

    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """
        Returns a list of all supported language codes (common codes, not NLLB codes)
        """
        return sorted(list(set(cls.LANGUAGE_MAPPING.keys())))

    @classmethod
    def get_nllb_code_mapping(cls) -> Dict[str, str]:
        """
        Returns the complete mapping of common codes to NLLB codes
        """
        return cls.LANGUAGE_MAPPING.copy()
