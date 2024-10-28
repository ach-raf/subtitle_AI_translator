from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from library.base_translator import BaseTranslator
from library.model_handler import ModelHandler
from typing import List, Optional
import re


class M2M100Translator(BaseTranslator):
    def load_model(self) -> None:

        model_path = ModelHandler.download_model(self.model_name)
        self.model = M2M100ForConditionalGeneration.from_pretrained(model_path).to(
            self.device
        )
        self.src_lang = "en"
        self.tgt_lang = "ar"
        self.tokenizer = M2M100Tokenizer.from_pretrained(model_path)
        self.tokenizer.src_lang = self.src_lang

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

    def simple_translate(self, text: str, tgt_lang: Optional[str] = None) -> str:
        try:
            target_lang = tgt_lang or self.tgt_lang
            encoded = self.tokenizer(text, return_tensors="pt").to(self.device)
            generated_tokens = self.model.generate(
                **encoded,
                forced_bos_token_id=self.tokenizer.get_lang_id(target_lang),
                num_beams=self.config.num_beams,
                num_return_sequences=self.config.num_return_sequences,
                length_penalty=self.config.length_penalty,
            )
            result = self.tokenizer.batch_decode(
                generated_tokens, skip_special_tokens=True
            )
            return result[0]  # Return the first (and typically only) translation
        except Exception as e:
            print(f"An error occurred during translation: {str(e)}")
            return text

    def translate(self, text: str, tgt_lang: Optional[str] = None) -> str:
        try:
            """if len(text.split()) > 50:
                text = text.replace("'", "'")
                print("Splitting text into chunks...")
                chunks = self.split_text(text)

                result = []
                for chunk in chunks:
                    if chunk["text"]:
                        translated_text = self.simple_translate(chunk["text"], tgt_lang)
                        result.append(translated_text)
                    if chunk["ends_with_newline"]:
                        result.append("\n")

                return "".join(result).rstrip()"""

            print("Translating text...")
            return self.simple_translate(text, tgt_lang)
        except Exception as e:
            print(f"An error occurred during translation: {str(e)}")
            return text

    def batch_translate(
        self, texts: List[str], tgt_lang: Optional[str] = None
    ) -> List[str]:
        target_lang = tgt_lang or self.tgt_lang
        encoded = self.tokenizer(
            texts, padding=True, truncation=True, return_tensors="pt"
        ).to(self.device)
        generated_tokens = self.model.generate(
            **encoded, forced_bos_token_id=self.tokenizer.get_lang_id(target_lang)
        )
        return self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
