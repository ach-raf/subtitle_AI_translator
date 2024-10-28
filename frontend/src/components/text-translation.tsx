"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { ArrowRightLeft, Copy, Wand2, Eraser, Volume2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { translateText, AIModel } from "@/services/api";
import { languages } from "@/models/languages";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const LOCAL_STORAGE_KEYS = {
  SOURCE_TEXT: "sourceText",
  TRANSLATED_TEXT: "translatedText",
  SOURCE_LANGUAGE: "sourceLanguage",
  TARGET_LANGUAGE: "targetLanguage",
  AI_MODEL: "aiModel",
};

const MAX_CHAR_COUNT = 5000;

interface TextTranslationComponentProps {
  selectedModel: AIModel;
  onModelChange: (model: AIModel) => void;
}

export function TextTranslationComponent({
  selectedModel,
  onModelChange,
}: TextTranslationComponentProps) {
  const [sourceText, setSourceText] = useState<string>(
    localStorage.getItem(LOCAL_STORAGE_KEYS.SOURCE_TEXT) || ""
  );
  const [translatedText, setTranslatedText] = useState<string>(
    localStorage.getItem(LOCAL_STORAGE_KEYS.TRANSLATED_TEXT) || ""
  );
  const [sourceLanguage, setSourceLanguage] = useState<string>(
    localStorage.getItem(LOCAL_STORAGE_KEYS.SOURCE_LANGUAGE) || "en"
  );
  const [targetLanguage, setTargetLanguage] = useState<string>(
    localStorage.getItem(LOCAL_STORAGE_KEYS.TARGET_LANGUAGE) || "es"
  );
  const [isTranslating, setIsTranslating] = useState(false);
  const [progress, setProgress] = useState(0);
  const { toast } = useToast();
  const sourceTextareaRef = useRef<HTMLTextAreaElement>(null);
  const translatedTextareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    localStorage.setItem(LOCAL_STORAGE_KEYS.SOURCE_TEXT, sourceText);
  }, [sourceText]);

  useEffect(() => {
    localStorage.setItem(LOCAL_STORAGE_KEYS.TRANSLATED_TEXT, translatedText);
  }, [translatedText]);

  useEffect(() => {
    localStorage.setItem(LOCAL_STORAGE_KEYS.SOURCE_LANGUAGE, sourceLanguage);
  }, [sourceLanguage]);

  useEffect(() => {
    localStorage.setItem(LOCAL_STORAGE_KEYS.TARGET_LANGUAGE, targetLanguage);
  }, [targetLanguage]);

  useEffect(() => {
    localStorage.setItem(LOCAL_STORAGE_KEYS.AI_MODEL, selectedModel);
  }, [selectedModel]);

  useEffect(() => {
    const resizeTextarea = (textarea: HTMLTextAreaElement | null) => {
      if (textarea) {
        textarea.style.height = "auto";
        textarea.style.height = `${Math.min(
          Math.max(textarea.scrollHeight, 300),
          800
        )}px`;
      }
    };

    resizeTextarea(sourceTextareaRef.current);
    resizeTextarea(translatedTextareaRef.current);
  }, [sourceText, translatedText]);

  const handleTranslate = async () => {
    if (!sourceText || !targetLanguage || sourceLanguage === targetLanguage)
      return;

    setIsTranslating(true);
    setProgress(0);
    try {
      const result = await translateText(
        sourceText,
        sourceLanguage,
        targetLanguage,
        selectedModel,
        (progress) => setProgress(progress)
      );
      setTranslatedText(result);
    } catch (error) {
      toast({
        title: "Translation failed",
        description: "An error occurred while translating the text.",
        variant: "destructive",
      });
    } finally {
      setIsTranslating(false);
      setProgress(100);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      toast({
        title: "Copied to clipboard",
        description: "The text has been copied to your clipboard.",
      });
    });
  };

  const handleSwapLanguages = () => {
    const tempLang = sourceLanguage;
    setSourceLanguage(targetLanguage);
    setTargetLanguage(tempLang);
    setSourceText(translatedText);
    setTranslatedText(sourceText);
  };

  const handleClear = (type: "source" | "translated") => {
    if (type === "source") {
      setSourceText("");
    } else {
      setTranslatedText("");
    }
  };

  const handleSpeak = (text: string, lang: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    window.speechSynthesis.speak(utterance);
  };

  const renderTextArea = (
    id: string,
    value: string,
    onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void,
    placeholder: string,
    isReadOnly: boolean,
    ref: React.RefObject<HTMLTextAreaElement>
  ) => (
    <Textarea
      id={id}
      ref={ref}
      className="min-h-[300px] max-h-[800px] resize-none"
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      readOnly={isReadOnly}
      maxLength={MAX_CHAR_COUNT}
    />
  );

  const renderActionButtons = (
    text: string,
    lang: string,
    type: "source" | "translated"
  ) => (
    <div className="flex space-x-2 mb-2">
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleClear(type)}
        title="Clear text"
      >
        <Eraser className="h-4 w-4 mr-2" />
        Clear
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleCopy(text)}
        title="Copy to clipboard"
      >
        <Copy className="h-4 w-4 mr-2" />
        Copy
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleSpeak(text, lang)}
        title="Listen"
      >
        <Volume2 className="h-4 w-4 mr-2" />
        Listen
      </Button>
    </div>
  );

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <h1 className="text-4xl font-bold text-center mb-8">
        AI-Powered Text Translator
      </h1>
      <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800 shadow-xl">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row justify-between items-center mb-6 space-y-4 md:space-y-0">
            <div className="flex items-center space-x-4 w-full md:w-auto">
              <Select value={sourceLanguage} onValueChange={setSourceLanguage}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Source" />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      {lang.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="icon"
                onClick={handleSwapLanguages}
              >
                <ArrowRightLeft className="h-4 w-4" />
              </Button>
              <Select value={targetLanguage} onValueChange={setTargetLanguage}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Target" />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      {lang.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center space-x-4">
              <Select value={selectedModel} onValueChange={onModelChange}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="AI Model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="opus">OPUS</SelectItem>
                  <SelectItem value="m2m100">M2M100</SelectItem>
                  <SelectItem value="nllb">NLLB</SelectItem>
                  <SelectItem value="madlad">MADLAD</SelectItem>
                </SelectContent>
              </Select>
              <Button
                onClick={handleTranslate}
                disabled={
                  !sourceText ||
                  !targetLanguage ||
                  sourceLanguage === targetLanguage ||
                  isTranslating
                }
                className="w-full md:w-auto"
              >
                {isTranslating ? "Translating..." : "Translate"}
                <Wand2 className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
          {isTranslating && (
            <Progress value={progress} className="w-full mb-4" />
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="source-text" className="text-lg font-semibold">
                Source Text
              </Label>
              {renderActionButtons(sourceText, sourceLanguage, "source")}
              {renderTextArea(
                "source-text",
                sourceText,
                (e) => setSourceText(e.target.value),
                "Enter text to translate...",
                false,
                sourceTextareaRef
              )}
              <div className="text-sm text-gray-500 mt-2">
                {sourceText.length}/{MAX_CHAR_COUNT} characters
              </div>
            </div>
            <div className="space-y-2">
              <Label
                htmlFor="translated-text"
                className="text-lg font-semibold"
              >
                Translated Text
              </Label>
              {renderActionButtons(
                translatedText,
                targetLanguage,
                "translated"
              )}
              {renderTextArea(
                "translated-text",
                translatedText,
                () => {},
                "Translation will appear here...",
                true,
                translatedTextareaRef
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
