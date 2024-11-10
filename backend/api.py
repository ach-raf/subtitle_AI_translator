from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
import uuid
from contextlib import asynccontextmanager

from library.config import TranslationConfig
from library.opus_translator import OpusTranslator
from library.M2M100_translator import M2M100Translator
from library.nllb_translator import NLLBTranslator
from library.madlad_translator import MadladTranslator
from library.hf_seamless_m4t import SeamlessTranslator
from library.faseeh_translator import FaseehTranslator
from library.subtitle_processor import SubtitleProcessor

from enum import Enum

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Subtitle Translation API",
    description="API for translating subtitles and text",
    version="1.0.0",
)

# Load environment variables
load_dotenv()
# Get origins from .env and split into list
origins = os.getenv("CORS_ORIGINS", "").split(",")

# Configure CORS
# Fallback if env variable is not set
if not origins or origins == [""]:
    origins = [
        "http://localhost:15571",
        "http://127.0.0.1:15571",
        "http://0.0.0.0:15571",
        "https://0.0.0.0:15571",
    ]
# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models


class AIModel(str, Enum):
    OPUS = "opus"
    M2M100 = "m2m100"
    NLLB = "nllb"
    MADLAD = "madlad"
    SEAMLESS = "seamless"
    DARIJA = "darija"
    FASEEH = "faseeh"


class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str
    model: AIModel


class BatchTranslationRequest(BaseModel):
    texts: List[str]
    source_lang: str
    target_lang: str
    model: AIModel


class TranslationResponse(BaseModel):
    translated_text: str


class BatchTranslationResponse(BaseModel):
    translated_texts: List[str]


class SubtitleTranslationRequest(BaseModel):
    unique_filename: str
    source_lang: str
    target_lang: str
    model: AIModel
    batch_size: Optional[int] = 15


# Global variables
translator: Optional[OpusTranslator] = None


# def get_translator(source_lang: str, target_lang: str):
#     global translator
#     # You might want to adjust the model selection logic based on language pairs
#     model_name = f"facebook/mbart-large-50-many-to-many-mmt"
#     model_name = f"Helsinki-NLP/opus-mt-mul-en"
#     model_name = f"facebook/m2m100_1.2B"
#     model_name = f"marefa-nlp/marefa-mt-en-ar"
#     model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
#     model_name = f"facebook/nllb-200-distilled-600M"
#     model_name = f"Helsinki-NLP/opus-mt-tc-big-{source_lang}-{target_lang}"

#     if translator is None or translator.model_name != model_name:
#         config = TranslationConfig()

#         """translator = M2M100Translator(
#             model_name=model_name, src_lang="en", tgt_lang="fr", config=config
#         )
#         translator.load_model()"""

#         translator = OpusTranslator(model_name, config)
#         # translator = NLLBTranslator(model_name, config)
#         translator.load_model()
#     return translator


def get_translator(source_lang: str, target_lang: str, model: AIModel):
    global translator
    config = TranslationConfig()

    if model == AIModel.OPUS:
        model_name = f"Helsinki-NLP/opus-mt-tc-big-{source_lang}-{target_lang}"
        translator = OpusTranslator(model_name, config)
    elif model == AIModel.M2M100:
        model_name = "facebook/m2m100_418M"
        translator = M2M100Translator(
            model_name, src_lang=source_lang, tgt_lang=target_lang, config=config
        )
    elif model == AIModel.NLLB:
        model_name = "facebook/nllb-200-distilled-600M"
        translator = NLLBTranslator(model_name, config)
    elif model == AIModel.MADLAD:
        # model_name = "google/madlad400-3b-mt"
        model_name = "santhosh/madlad400-3b-ct2"
        translator = MadladTranslator(model_name, config)

    elif model == AIModel.SEAMLESS:
        # model_name = "facebook/hf-seamless-m4t-large"
        model_name = "facebook/hf-seamless-m4t-medium"
        translator = SeamlessTranslator(model_name, config)

    elif model == AIModel.DARIJA:
        # model_name = f"lachkarsalim/Helsinki-translation-English_Moroccan-Arabic"
        model_name = "Trabis/Helsinki-NLPopus-mt-tc-big-en-moroccain_dialect"
        translator = OpusTranslator(model_name, config)
    elif model == AIModel.FASEEH:
        model_name = "Abdulmohsena/Faseeh"
        translator = FaseehTranslator(model_name, config)

    translator.load_model()
    return translator


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create necessary directories on startup
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("downloads", exist_ok=True)
    yield
    # Cleanup can be added here if needed


@app.get("/")
async def root():
    return {"message": "Subtitle Translation API is running"}


@app.post("/upload-subtitle")
async def upload_subtitle(file: UploadFile = File(...)):
    try:
        # Generate a unique filename to prevent conflicts
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_location = f"uploads/{unique_filename}"

        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())

        return {
            "message": f"Subtitle file uploaded successfully",
            "file_path": file_location,
            "original_filename": file.filename,
            "unique_filename": unique_filename,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate-subtitle")
async def translate_subtitle(
    request: SubtitleTranslationRequest, background_tasks: BackgroundTasks
):
    try:
        input_path = f"uploads/{request.unique_filename}"
        if not os.path.exists(input_path):
            raise HTTPException(
                status_code=404, detail="Uploaded subtitle file not found"
            )

        output_filename = f"{uuid.uuid4()}.srt"
        output_path = f"downloads/{output_filename}"

        # Add the translation process to background tasks
        background_tasks.add_task(
            process_translation,
            request.source_lang,
            request.target_lang,
            input_path,
            output_path,
            request.batch_size,
            request.model,
        )

        # Return a message immediately with the filename where the translated subtitle will be available
        return {
            "message": "Subtitle translation started",
            "download_filename": output_filename,
            "status": "Processing",
        }

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def process_translation(
    source_lang, target_lang, input_path, output_path, batch_size, model: AIModel
):
    print(
        f"process_translation, source_lang: {source_lang}, target_lang: {target_lang}, input_path: {input_path}, output_path: {output_path}, batch_size: {batch_size}, model: {model}"
    )
    try:
        translator = get_translator(source_lang, target_lang, model)
        processor = SubtitleProcessor(
            translator=translator,
            batch_size=batch_size,
            batch_processing=False,
            source_lang=source_lang,
            target_lang=target_lang,
        )

        processor.process_file(
            input_path=input_path,
            output_path=output_path,
        )
    except Exception as e:
        print(f"An error occurred in the background process: {str(e)}")


@app.get("/download-subtitle/{filename}")
async def download_subtitle(filename: str):
    file_path = f"downloads/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, detail="Translated subtitle file not found"
        )

    return FileResponse(file_path, media_type="application/x-subrip", filename=filename)


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    try:
        translator = get_translator(
            request.source_lang, request.target_lang, request.model
        )
        translated_text = translator.translate(
            request.text.lower(), request.source_lang, request.target_lang
        )
        if isinstance(translated_text, list):
            translated_text = translated_text[0] if translated_text else ""
        return TranslationResponse(translated_text=translated_text)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-translate", response_model=BatchTranslationResponse)
async def batch_translate_texts(request: BatchTranslationRequest):
    try:
        translator = get_translator(
            request.source_lang, request.target_lang, request.model
        )
        translated_texts = translator.batch_translate(
            request.texts, request.source_lang, request.target_lang
        )
        return BatchTranslationResponse(translated_texts=translated_texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=36004,
        reload=True,
    )
