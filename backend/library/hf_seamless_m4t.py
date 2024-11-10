from typing import List, Union, Optional, Dict
from transformers import AutoProcessor, SeamlessM4TModel
import torch
from library.base_translator import BaseTranslator
from library.config import TranslationConfig
from library.model_handler import ModelHandler


class SeamlessTranslator(BaseTranslator):
    # Language code mapping from common codes to Seamless codes
    LANGUAGE_CODE_MAP = {
        # Common English variations to 'eng'
        "en": "eng",
        "en-US": "eng",
        "en-GB": "eng",
        # Arabic variations to 'arb' (Modern Standard Arabic)
        "ar": "arb",
        "ar-SA": "arb",
        # Chinese variations
        "zh": "cmn",
        "zh-CN": "cmn",
        "zh-TW": "cmn_Hant",
        # French variations
        "fr": "fra",
        "fr-FR": "fra",
        # Spanish variations
        "es": "spa",
        "es-ES": "spa",
        # German variations
        "de": "deu",
        "de-DE": "deu",
        # Japanese
        "ja": "jpn",
        # Korean
        "ko": "kor",
        # Russian
        "ru": "rus",
        # Portuguese
        "pt": "por",
        "pt-BR": "por",
        "pt-PT": "por",
        # Italian
        "it": "ita",
        # Dutch
        "nl": "nld",
        # Turkish
        "tr": "tur",
        # Vietnamese
        "vi": "vie",
        # Thai
        "th": "tha",
        # Indonesian
        "id": "ind",
        # Hindi
        "hi": "hin",
        # Bengali
        "bn": "ben",
    }

    def __init__(
        self,
        model_name: str = "facebook/hf-seamless-m4t-medium",
        config: Optional[TranslationConfig] = None,
    ):
        super().__init__(model_name, config)
        self.processor = None

    def load_model(self) -> None:
        """Load the model and processor from the specified path."""
        model_path = ModelHandler.download_model(self.model_name)
        self.model = SeamlessM4TModel.from_pretrained(model_path).to(self.device)
        self.processor = AutoProcessor.from_pretrained(model_path)

    def _map_language_code(self, code: str) -> str:
        """
        Map common language codes to Seamless-specific codes.

        Args:
            code: Input language code (e.g., 'en', 'ar')

        Returns:
            Seamless-specific language code (e.g., 'eng', 'arb')
        """
        return self.LANGUAGE_CODE_MAP.get(code.lower(), code)

    def translate(
        self, text: str, source_lang: str = "eng", target_lang: str = "fra"
    ) -> str:
        """
        Translate text to target language.

        Args:
            text: Input text
            source_lang: Source language code (common format like 'en' or Seamless format like 'eng')
            target_lang: Target language code (common format like 'fr' or Seamless format like 'fra')

        Returns:
            Translated text
        """
        # Map language codes to Seamless format
        src_lang = self._map_language_code(source_lang)
        tgt_lang = self._map_language_code(target_lang)

        try:
            # Process input
            input_data = self.processor(
                text=text, src_lang=src_lang, return_tensors="pt"
            ).to(self.device)

            # Generate translation
            output = self.model.generate(
                **input_data,
                tgt_lang=tgt_lang,
                num_beams=self.config.num_beams or 5,
                do_sample=True,
                generate_speech=False,
            )

            # Process output
            tokens = output[0].cpu().squeeze().detach().tolist()
            return self.processor.decode(tokens, skip_special_tokens=True)
        except Exception as e:
            print(f"An error occurred during translation: {str(e)}")
            return text

    def batch_translate(
        self, texts: List[str], source_lang: str = "eng", target_lang: str = "arb"
    ) -> List[str]:
        """
        Translate a batch of texts.

        Args:
            texts: List of input texts to translate
            source_lang: Source language code (common format like 'en' or Seamless format like 'eng')
            target_lang: Target language code (common format like 'fr' or Seamless format like 'fra')

        Returns:
            List of translated texts
        """
        # TODO: Implement batch translation

        return [self.translate(text, source_lang, target_lang) for text in texts]
