import re
from typing import List, Dict, Union
from dataclasses import dataclass


@dataclass
class Subtitle:
    index: int
    timestamp: str
    text: str


class SubtitleProcessor:
    def __init__(self, translator, batch_size: int = 5, batch_processing: bool = False):
        self.translator = translator
        self.batch_size = batch_size
        self.batch_processing = batch_processing

    def process_file(self, input_path: str, output_path: str) -> None:
        subtitles = self._extract_subtitles(input_path)
        translated_subtitles = self._process_subtitles(subtitles)
        self._write_subtitles(translated_subtitles, output_path)

    def _process_subtitles(self, subtitles: List[Subtitle]) -> List[Subtitle]:
        if self.batch_processing:
            return self._batch_process_subtitles(subtitles)
        return self._individual_process_subtitles(subtitles)

    def _batch_process_subtitles(self, subtitles: List[Subtitle]) -> List[Subtitle]:
        print("Batch processing subtitles...")
        try:
            model_inputs = []
            results = []
            total_subtitles = len(subtitles)

            for i, subtitle in enumerate(subtitles):
                print(f"Processing subtitle {i+1}/{total_subtitles}")
                model_inputs.append(subtitle.text)

                # Process when batch is full or at the end
                if len(model_inputs) == self.batch_size or i == total_subtitles - 1:
                    translations = self.translator.batch_translate(model_inputs)

                    # Process translations
                    for translated_text in translations:
                        # Check and fix leading dot
                        if translated_text.startswith("."):
                            translated_text = translated_text[1:] + "."
                        results.append(translated_text)

                    model_inputs = []

            # Update subtitle texts with translations
            for subtitle, translation in zip(subtitles, results):
                subtitle.text = translation

            return subtitles

        except Exception as e:
            print(f"An error occurred during batch processing: {str(e)}")
            return subtitles

    def _process_batch(self, texts: List[str]) -> List[str]:
        translations = self.translator.batch_translate(texts)
        return [self._format_translation(t) for t in translations]

    def _individual_process_subtitles(
        self, subtitles: List[Subtitle]
    ) -> List[Subtitle]:
        total_subtitles = len(subtitles)

        for i, subtitle in enumerate(subtitles):
            print(f"Processing subtitle {subtitle.index}/{total_subtitles}")
            translation = self.translator.translate(subtitle.text)

            if isinstance(translation, list):
                translation = translation[0]

            subtitle.text = translation

        return subtitles

    @staticmethod
    def _format_translation(text: str) -> str:
        if text.startswith("."):
            return f"{text[1:]}."
        return text

    @staticmethod
    def _extract_subtitles(file_path: str) -> List[Subtitle]:
        pattern = (
            r"(\d+)\s*\n"  # Match the index followed by optional whitespace and a newline
            r"(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\s*\n"  # Match the timestamp
            r"(.*?)\s*(?=\n{2}|\r?\n*$)"  # Match the text until two newlines or end of string
        )
        subtitles = []

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                srt_content = file.read()

            # Normalize line endings to \n
            srt_content = re.sub(r"\r\n|\r", "\n", srt_content)

            for match in re.finditer(pattern, srt_content, re.DOTALL):
                # Clean up text by stripping it and removing <i> tags
                text = re.sub(r"</?i>", "", match.group(3)).strip()

                subtitle = Subtitle(
                    index=int(match.group(1)),
                    timestamp=match.group(2),
                    text=text,
                )
                subtitles.append(subtitle)

        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

        if not subtitles:
            print("No subtitles found.")

        return subtitles

    @staticmethod
    def _write_subtitles(subtitles: List[Subtitle], file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as file:
            for subtitle in subtitles:
                file.write(f"{subtitle.index}\n")
                file.write(f"{subtitle.timestamp}\n")
                file.write(f"{subtitle.text}\n\n")
