# base_translator.py
from abc import ABC, abstractmethod
from typing import List, Union
from library.config import TranslationConfig
from library.model_handler import ModelHandler
from transformers import PreTrainedModel, PreTrainedTokenizer
from typing import Optional


class BaseTranslator(ABC):
    def __init__(self, model_name: str, config: Optional[TranslationConfig] = None):
        self.model_name = model_name
        self.config = config or TranslationConfig()
        self.model: Optional[PreTrainedModel] = None
        self.tokenizer: Optional[PreTrainedTokenizer] = None
        self.device = ModelHandler.get_device()

    @abstractmethod
    def load_model(self) -> None:
        pass

    @abstractmethod
    def translate(
        self, text: str, source_lang: str = "en", target_lang: str = "ar"
    ) -> Union[str, List[str]]:
        pass

    @abstractmethod
    def batch_translate(self, texts: List[str]) -> List[str]:
        pass
