import ctranslate2
from sentencepiece import SentencePieceProcessor
from library.base_translator import BaseTranslator
from library.model_handler import ModelHandler
from typing import List
import re


class MadladTranslator(BaseTranslator):

    def load_model(self) -> None:
        model_path = ModelHandler.download_model(self.model_name)
        self.translator = ctranslate2.Translator(str(model_path))
        self.tokenizer = SentencePieceProcessor()
        self.tokenizer.load(f"{model_path}/sentencepiece.model")

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

    def simple_translate(self, text: str, target_lang: str) -> str:
        input_tokens = self.tokenizer.encode(f"<2{target_lang}> {text}", out_type=str)
        results = self.translator.translate_batch(
            [input_tokens],
            batch_type="tokens",
            max_batch_size=1024,
            beam_size=self.config.num_beams,
            no_repeat_ngram_size=1,
            repetition_penalty=2,
        )
        translated_sentence = self.tokenizer.decode(results[0].hypotheses[0])
        return translated_sentence

    def translate(
        self, text: str, source_lang: str = "en", target_lang: str = "ar"
    ) -> str:
        try:
            if len(text.split()) > 250:
                chunks = self.split_text(text)
                result = []
                for chunk in chunks:
                    if chunk["text"]:
                        translated_text = self.simple_translate(
                            chunk["text"], target_lang
                        )
                        result.append(translated_text)
                    if chunk["ends_with_newline"]:
                        result.append("\n")
                return "".join(result).rstrip()
            return self.simple_translate(text, target_lang)
        except Exception as e:
            print(f"An error occurred during translation: {str(e)}")
            return text

    def batch_translate(self, inputs: List[str], target_lang: str = "ar") -> List[str]:
        input_tokens_batch = [
            self.tokenizer.encode(f"<2{target_lang}> {text}", out_type=str)
            for text in inputs
        ]
        results = self.translator.translate_batch(
            input_tokens_batch,
            batch_type="tokens",
            max_batch_size=1024,
            beam_size=self.config.num_beams,
            no_repeat_ngram_size=1,
            repetition_penalty=2,
        )
        translated_sentences = [
            self.tokenizer.decode(result.hypotheses[0]) for result in results
        ]
        return translated_sentences
