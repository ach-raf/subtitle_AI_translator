# config.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranslationConfig:
    batch_size: int = 5
    max_new_tokens: int = 250
    num_beams: int = 8
    num_return_sequences: int = 1
    length_penalty: float = 0.1
