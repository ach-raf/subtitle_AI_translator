# model_handler.py
import os
import shutil
from pathlib import Path
import huggingface_hub as hub
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer


class ModelHandler:
    @staticmethod
    def download_model(model_name: str) -> Path:
        model_path = Path("models") / model_name.split("/")[-1]

        if not model_path.exists():
            try:
                # Exclude files you don't need: flax_model.msgpack and tf_model.h5, rust_model.ot,model.safetensors
                ignore_patterns = [
                    "flax_model.msgpack",
                    "tf_model.h5",
                    "rust_model.ot",
                    "model.safetensors",
                    "model.npz.best-chrf.npz",
                    "325orch_model.bin",
                ]

                # Download only the necessary files
                dirname = hub.snapshot_download(
                    model_name,
                    ignore_patterns=ignore_patterns,
                    force_download=True,
                )

                # Ensure dirname is not None
                if dirname is None or not Path(dirname).exists():
                    raise ValueError(
                        f"Model download failed. No valid directory found for model: {model_name}"
                    )

                # Copy the downloaded files to the models directory
                shutil.copytree(dirname, model_path)

            except Exception as e:
                print(f"Error during model download: {e}")
                raise e  # Re-raise the error after logging it

        return model_path

    @staticmethod
    def get_device() -> torch.device:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
