# mbart_translator.py
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from library.base_translator import BaseTranslator
from library.model_handler import ModelHandler
from typing import List


class MBartTranslator(BaseTranslator):
    def load_model(self) -> None:
        model_path = ModelHandler.download_model(self.model_name)
        self.model = MBartForConditionalGeneration.from_pretrained(model_path).to(
            self.device
        )
        self.tokenizer = MBart50TokenizerFast.from_pretrained(
            model_path,
            clean_up_tokenization_spaces=False,
            src_lang="en_XX",
            tgt_lang="ar_AR",
            ignore_mismatched_sizes=True,
        )

        self.tokenizer.src_lang = "en_XX"
        self.tokenizer.tgt_lang = "ar_AR"

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> List[str]:
        # Set the source language
        self.tokenizer.src_lang = src_lang
        input_ids = self.tokenizer(text, return_tensors="pt").input_ids.to(self.device)

        # Translate to target language
        generated_tokens = self.model.generate(
            input_ids=input_ids,
            forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_lang],
            max_new_tokens=self.config.max_new_tokens,
            num_beams=self.config.num_beams,
            num_return_sequences=self.config.num_return_sequences,
            length_penalty=self.config.length_penalty,
        )

        return [
            self.tokenizer.decode(t, skip_special_tokens=True) for t in generated_tokens
        ]

    def batch_translate(
        self, texts: List[str], src_lang: str, tgt_lang: str
    ) -> List[str]:
        # Set the source language
        self.tokenizer.src_lang = src_lang
        input_ids = self.tokenizer(
            texts, padding=True, truncation=True, return_tensors="pt"
        ).input_ids.to(self.device)

        # Translate to target language
        generated_tokens = self.model.generate(
            input_ids=input_ids,
            forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_lang],
        )

        return self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
