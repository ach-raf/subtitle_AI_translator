# nllb_translator.py
from transformers import pipeline
import torch
from transformers.utils import logging
from library.base_translator import BaseTranslator
from library.model_handler import ModelHandler
from library.language_utils import LanguageUtils
from typing import List, Union

logging.set_verbosity_error()


class NLLBTranslator(BaseTranslator):

    def __init__(self, model_name: str, config=None):
        super().__init__(model_name, config)
        self.translator = None

    def load_model(self) -> None:
        model_path = ModelHandler.download_model(self.model_name)
        self.translator = pipeline(
            task="translation",
            model=model_path,
            torch_dtype=torch.bfloat16,
            device=self.device,
        )

    def translate(
        self, text: str, source_lang: str = "en", target_lang: str = "ar"
    ) -> str:
        try:
            nllb_src = LanguageUtils.get_nllb_language_code(source_lang)
            nllb_tgt = LanguageUtils.get_nllb_language_code(target_lang)
            print(f"Translating from {nllb_src} to {nllb_tgt}")
            output = self.translator(
                text,
                src_lang=nllb_src,
                tgt_lang=nllb_tgt,
                max_length=self.config.max_new_tokens,
                num_beams=self.config.num_beams,
                length_penalty=self.config.length_penalty,
            )
            return output[0]["translation_text"]
        except Exception as e:
            print(f"An error occurred during translation: {str(e)}")
            return text

    def batch_translate(
        self, texts: List[str], source_lang: str = "en", target_lang: str = "ar"
    ) -> List[str]:
        try:
            nllb_src = LanguageUtils.get_nllb_language_code(source_lang)
            nllb_tgt = LanguageUtils.get_nllb_language_code(target_lang)
            print(f"Translating from {nllb_src} to {nllb_tgt}")

            outputs = self.translator(
                texts,
                src_lang=nllb_src,
                tgt_lang=nllb_tgt,
                max_length=self.config.max_new_tokens,
                num_beams=self.config.num_beams,
                length_penalty=self.config.length_penalty,
            )
            return [output["translation_text"] for output in outputs]
        except Exception as e:
            print(f"An error occurred during batch translation: {str(e)}")
            return texts
