from library.base_translator import BaseTranslator
from library.model_handler import ModelHandler
from typing import List, Optional
import re
from llama_cpp import Llama
from sentencepiece import SentencePieceProcessor
import torch


class LlamaCppMadladTranslator(BaseTranslator):
    def __init__(self, model_name: str, config=None):
        super().__init__(model_name, config)
        self.llm: Optional[Llama] = None
        self.tokenizer: Optional[SentencePieceProcessor] = None
        self.model_path = None

        # Set default parameters for translation
        self.max_tokens = config.max_tokens if config else 2048
        self.temperature = config.temperature if config else 0.1
        self.top_p = config.top_p if config else 0.95
        self.n_ctx = config.n_ctx if config else 4096

    def load_model(self) -> None:
        """
        Load the GGUF model and its associated tokenizer.
        """
        self.model_path = ModelHandler.download_model(self.model_name)

        # Find the GGUF file
        gguf_files = list(self.model_path.glob("*.gguf"))
        if not gguf_files:
            raise FileNotFoundError(f"No GGUF model found in {self.model_path}")

        # Initialize llama.cpp
        n_gpu_layers = -1 if self.device.type == "cuda" else 0

        self.llm = Llama(
            model_path=str(gguf_files[0]),
            n_ctx=self.n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
        )

        # Load SentencePiece tokenizer if available
        tokenizer_path = self.model_path / "sentencepiece.model"
        if tokenizer_path.exists():
            self.tokenizer = SentencePieceProcessor()
            self.tokenizer.load(str(tokenizer_path))

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
        """Translate a single piece of text using llama.cpp."""
        prompt = f"""Translate the following text to {target_lang}. 
Only output the translation, without any additional text or explanation.

Text: {text}

Translation:"""

        response = self.llm(
            prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            echo=False,
            stop=["Text:", "\n\n"],
        )

        if response and "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["text"].strip()
        return text

    def translate(
        self, text: str, source_lang: str = "en", target_lang: str = "ar"
    ) -> str:
        """
        Translate text from source language to target language.
        Handles long texts by splitting them into chunks.
        """
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
        """Translate multiple texts."""
        return [self.translate(text, target_lang=target_lang) for text in inputs]
