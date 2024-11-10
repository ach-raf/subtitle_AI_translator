import axios from "axios";
import { AIModel } from "@/types/ai-model";
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

export const translateText = async (
  text: string,
  sourceLang: string,
  targetLang: string,
  model: AIModel,
  onProgress: (progress: number) => void
) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/translate`,
      {
        text,
        source_lang: sourceLang,
        target_lang: targetLang,
        model,
      },
      {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(percentCompleted);
          }
        },
      }
    );
    onProgress(100); // Ensure we reach 100% when the request is complete
    return response.data.translated_text;
  } catch (error) {
    console.error("Translation error:", error);
    throw error;
  }
};

export const uploadSubtitle = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await axios.post(
    `${API_BASE_URL}/upload-subtitle`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );
  return response.data;
};

export const translateSubtitle = async (
  uniqueFilename: string,
  sourceLang: string,
  targetLang: string,
  model: AIModel,
  batchSize: number = 2
) => {
  const response = await axios.post(
    `${API_BASE_URL}/translate-subtitle`,
    {
      unique_filename: uniqueFilename,
      source_lang: sourceLang,
      target_lang: targetLang,
      model,
      batch_size: batchSize,
    },
    {
      timeout: 120000, // Increase to 120 seconds, adjust as needed
    }
  );
  return response.data;
};

export const downloadSubtitle = async (fileName: string) => {
  const response = await axios.get(
    `${API_BASE_URL}/download-subtitle/${fileName}`,
    { responseType: "blob" }
  );
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", fileName);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

export const fetchTranslatedSubtitles = async (fileName: string) => {
  const response = await axios.get(
    `${API_BASE_URL}/download-subtitle/${fileName}`,
    { responseType: "text" }
  );
  return response.data;
};
