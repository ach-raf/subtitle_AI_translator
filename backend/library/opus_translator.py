# opus_translator.py
from transformers import MarianTokenizer, MarianMTModel
from library.base_translator import BaseTranslator
from library.model_handler import ModelHandler
from typing import List
import re


class OpusTranslator(BaseTranslator):
    def load_model(self) -> None:
        model_path = ModelHandler.download_model(self.model_name)
        self.model = MarianMTModel.from_pretrained(model_path).to(self.device)
        self.tokenizer = MarianTokenizer.from_pretrained(
            model_path, clean_up_tokenization_spaces=False
        )

    def split_text(self, text: str, word_limit: int = 250) -> List[dict]:
        """Split text into chunks of the specified word limit, tracking line breaks."""
        chunks = []
        current_chunk = {"text": "", "ends_with_newline": False}
        current_word_count = 0

        paragraphs = text.split("\n")

        for i, paragraph in enumerate(paragraphs):
            words = paragraph.split()

            if not words:  # Empty paragraph (just a newline)
                if current_chunk["text"]:
                    current_chunk["ends_with_newline"] = True
                    chunks.append(current_chunk)
                    current_chunk = {"text": "", "ends_with_newline": False}
                    current_word_count = 0
                chunks.append({"text": "", "ends_with_newline": True})
                continue

            start = 0
            while start < len(words):
                remaining_words = word_limit - current_word_count
                end = min(start + remaining_words, len(words))

                chunk_text = " ".join(words[start:end])

                # Try to find the last punctuation mark within the chunk
                match = re.search(r"([.!?])\s", chunk_text)
                if match and start + len(chunk_text[: match.end()].split()) < len(
                    words
                ):
                    end = start + len(chunk_text[: match.end()].split())
                    chunk_text = " ".join(words[start:end])

                if current_chunk["text"]:
                    current_chunk["text"] += " "
                current_chunk["text"] += chunk_text
                current_word_count += len(chunk_text.split())

                if current_word_count >= word_limit or end == len(words):
                    if i < len(paragraphs) - 1 or end == len(words):
                        current_chunk["ends_with_newline"] = True
                    chunks.append(current_chunk)
                    current_chunk = {"text": "", "ends_with_newline": False}
                    current_word_count = 0

                start = end

        if current_chunk["text"]:
            chunks.append(current_chunk)

        return chunks

    def simple_translate(self, text: str) -> str:
        text = text.lower()
        try:
            input_ids = self.tokenizer(text, return_tensors="pt").input_ids.to(
                self.device
            )
            translated = self.model.generate(
                input_ids=input_ids,
                # max_new_tokens=self.config.max_new_tokens,
                num_beams=self.config.num_beams,
                num_return_sequences=self.config.num_return_sequences,
                length_penalty=self.config.length_penalty,
            )
            result = [
                self.tokenizer.decode(t, skip_special_tokens=True) for t in translated
            ]
            return result
        except Exception as e:
            print(f"An error occurred during translation: {str(e)}")
            return text

    def translate(
        self, text: str, source_lang: str = "en", target_lang: str = "ar"
    ) -> str:
        try:
            print(len(text.split()))
            if len(text.split()) > 250:
                text = text.replace("'", "'")
                print("Splitting text into chunks...")
                chunks = self.split_text(text)

                result = []
                for chunk in chunks:
                    if chunk["text"]:
                        translated_text = self.simple_translate(chunk["text"])[0]
                        result.append(translated_text)
                    if chunk["ends_with_newline"]:
                        result.append("\n")

                return "".join(result).rstrip()

            print("Translating text...")
            return self.simple_translate(text)[0]
        except Exception as e:
            print(f"An error occurred during translation: {str(e)}")
            return text

    def batch_translate(self, inputs):
        input_ids = self.tokenizer(
            inputs, padding=True, truncation=True, return_tensors="pt"
        ).input_ids.to(self.device)
        inputs = {"input_ids": input_ids}
        translated = self.model.generate(**inputs)
        translations = self.tokenizer.batch_decode(translated, skip_special_tokens=True)
        return translations
