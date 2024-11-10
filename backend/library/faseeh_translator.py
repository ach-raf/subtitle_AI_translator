from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, GenerationConfig
import torch
from library.base_translator import BaseTranslator
from library.model_handler import ModelHandler
from typing import List


class FaseehTranslator(BaseTranslator):
    def __init__(self, model_name: str = "Abdulmohsena/Faseeh", config=None):
        super().__init__(model_name, config)
        self.tokenizer = None
        self.model = None
        self.generation_config = None

    def load_model(self) -> None:
        """Load the Faseeh model, tokenizer and generation config"""
        model_path = ModelHandler.download_model(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path, src_lang="eng_Latn", tgt_lang="arb_Arab"
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_path, torch_dtype=torch.bfloat16, device_map=self.device
        )
        self.generation_config = GenerationConfig.from_pretrained(model_path)

    def translate(
        self, text: str, source_lang: str = "en", target_lang: str = "ar"
    ) -> str:
        """
        Translate a single text using Faseeh model

        Args:
            text: Text to translate
            source_lang: Source language (only supports 'en')
            target_lang: Target language (only supports 'ar')

        Returns:
            Translated text
        """
        try:
            if source_lang != "en" or target_lang != "ar":
                raise ValueError("Faseeh only supports English to Arabic translation")

            print(f"Translating from English to Arabic using Faseeh")
            encoded = self.tokenizer(text, return_tensors="pt").to(self.device)

            generated_tokens = self.model.generate(
                **encoded,
                generation_config=self.generation_config,
                max_length=self.config.max_new_tokens,
                num_beams=self.config.num_beams,
                length_penalty=self.config.length_penalty,
            )

            return self.tokenizer.decode(generated_tokens[0], skip_special_tokens=True)

        except Exception as e:
            print(f"An error occurred during translation: {str(e)}")
            return text

    def batch_translate(
        self, texts: List[str], source_lang: str = "en", target_lang: str = "ar"
    ) -> List[str]:
        """
        Translate a batch of texts using Faseeh model

        Args:
            texts: List of texts to translate
            source_lang: Source language (only supports 'en')
            target_lang: Target language (only supports 'ar')

        Returns:
            List of translated texts
        """
        try:
            if source_lang != "en" or target_lang != "ar":
                raise ValueError("Faseeh only supports English to Arabic translation")

            print(f"Batch translating from English to Arabic using Faseeh")
            results = []

            # Process each text individually since the model expects single inputs
            for text in texts:
                encoded = self.tokenizer(text, return_tensors="pt").to(self.device)
                generated_tokens = self.model.generate(
                    **encoded,
                    generation_config=self.generation_config,
                    max_length=self.config.max_new_tokens,
                    num_beams=self.config.num_beams,
                    length_penalty=self.config.length_penalty,
                )
                results.append(
                    self.tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
                )

            return results

        except Exception as e:
            print(f"An error occurred during batch translation: {str(e)}")
            return texts
