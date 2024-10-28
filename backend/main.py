from library.config import TranslationConfig
from library.opus_translator import OpusTranslator
from library.subtitle_processor import SubtitleProcessor
from typing import List


# Example usage
class TranslatorExample:
    def batch_translate(self, texts: List[str]) -> List[str]:
        # Simulated translation
        return [f"Translated: {text}" for text in texts]

    def translate(self, text: str) -> str:
        return f"Translated: {text}"


# main.py
def main():
    config = TranslationConfig()
    translator = OpusTranslator("Helsinki-NLP/opus-mt-en-fr", config)
    translator.load_model()

    # Example usage
    test_texts = ["Hello, how are you?", "This is a test."]
    translated = translator.batch_translate(test_texts)
    print(translated)


def main_subtitles():
    # Example usage
    config = TranslationConfig()
    translator = OpusTranslator("Helsinki-NLP/opus-mt-en-fr", config)
    translator.load_model()
    processor = SubtitleProcessor(
        translator=translator, batch_size=15, batch_processing=True
    )

    try:
        processor.process_file(
            input_path="./Flex x Cop (2024) - S01E01 - - Episode 1 [WEBDL-1080p][8bit][h264][AAC 2.0][KO]-EDITH.srt",
            output_path="./output.srt",
        )
        print("Translation completed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main_subtitles()
