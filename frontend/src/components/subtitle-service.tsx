import { useState, useCallback, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Upload, Globe, Download, ArrowRightLeft, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  uploadSubtitle,
  translateSubtitle,
  downloadSubtitle,
  fetchTranslatedSubtitles,
} from "@/services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { languages } from "@/types/languages";
import SubtitleDisplayComponent from "@/components/subtitle-display";
import { AIModel } from "@/types/ai-model";
import { AIModelSelector } from "@/components/ai-model-selector";

interface SubtitleServiceComponentProps {
  selectedModel: AIModel;
  onModelChange: (model: AIModel) => void;
}

export function SubtitleServiceComponent({
  selectedModel,
  onModelChange,
}: SubtitleServiceComponentProps) {
  const [file, setFile] = useState<File | null>(null);
  const [inputSubtitles, setInputSubtitles] = useState("");
  const [translatedSubtitles, setTranslatedSubtitles] = useState("");
  const [sourceLanguage, setSourceLanguage] = useState(() => {
    return localStorage.getItem("sourceLanguage") || "en";
  });
  const [targetLanguage, setTargetLanguage] = useState(() => {
    return localStorage.getItem("targetLanguage") || "";
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [outputFileName, setOutputFileName] = useState("");
  const [uniqueFilename, setUniqueFilename] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [showTranslationSection, setShowTranslationSection] = useState(false);
  const translationSectionRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    localStorage.setItem("sourceLanguage", sourceLanguage);
  }, [sourceLanguage]);

  useEffect(() => {
    localStorage.setItem("targetLanguage", targetLanguage);
  }, [targetLanguage]);

  useEffect(() => {
    if (showTranslationSection && translationSectionRef.current) {
      translationSectionRef.current.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }, [showTranslationSection]);

  const clearAll = () => {
    setInputSubtitles("");
    setTranslatedSubtitles("");
    setOutputFileName("");
    setUniqueFilename("");
    setShowTranslationSection(false);
  };

  const clearTranslation = () => {
    setTranslatedSubtitles("");
    setOutputFileName("");
  };

  const processFile = useCallback(
    async (uploadedFile: File) => {
      setFile(uploadedFile);
      try {
        const result = await uploadSubtitle(uploadedFile);
        setUniqueFilename(result.unique_filename);
        toast({
          title: "File uploaded",
          description: "Subtitle file has been uploaded successfully.",
        });
        const reader = new FileReader();
        reader.onload = (e) => {
          setInputSubtitles(e.target?.result as string);
          setShowTranslationSection(true);
        };
        reader.readAsText(uploadedFile);
      } catch (error) {
        toast({
          title: "Upload failed",
          description: "An error occurred while uploading the file.",
          variant: "destructive",
        });
      }
    },
    [toast]
  );

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = event.target.files?.[0];
    if (uploadedFile) {
      processFile(uploadedFile);
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);

      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) {
        processFile(droppedFile);
      }
    },
    [processFile]
  );

  const handleTranslate = async () => {
    if (!uniqueFilename || !targetLanguage) return;

    setIsProcessing(true);
    try {
      const result = await translateSubtitle(
        uniqueFilename,
        sourceLanguage,
        targetLanguage,
        selectedModel,
        2
      );
      setOutputFileName(result.download_filename);

      // Poll to check if translation is complete
      const intervalId = setInterval(async () => {
        try {
          const translatedContent = await fetchTranslatedSubtitles(
            result.download_filename
          );
          if (translatedContent) {
            setTranslatedSubtitles(translatedContent);
            toast({
              title: "Translation complete",
              description: "Subtitles have been translated successfully.",
            });
            clearInterval(intervalId); // Stop polling once translation is complete
          }
        } catch (pollError) {
          // Translation is still processing, continue polling
          console.log("Polling for translation...");
          console.error(pollError);
        }
      }, 6000); // Poll every 6 seconds
    } catch (error) {
      toast({
        title: "Translation failed",
        description: "An error occurred while translating the subtitles.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = async () => {
    if (!outputFileName) return;

    try {
      await downloadSubtitle(outputFileName);
      toast({
        title: "Download started",
        description: "Your translated subtitles are being downloaded.",
      });
    } catch (error) {
      toast({
        title: "Download failed",
        description: "An error occurred while downloading the file.",
        variant: "destructive",
      });
    }
  };

  const handleSwapLanguages = () => {
    const tempLang = sourceLanguage;
    setSourceLanguage(targetLanguage);
    setTargetLanguage(tempLang);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-[1920px]">
      <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800 shadow-xl">
        <CardHeader className="flex flex-row justify-between items-center">
          <CardTitle className="text-4xl font-bold">Subtitle Wizard</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={clearAll}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="h-5 w-5 mr-1" /> Clear All
          </Button>
        </CardHeader>
        <CardContent className="p-8 space-y-10">
          <div className="flex flex-col items-center">
            <Label
              htmlFor="file-upload"
              className="text-xl font-medium text-gray-700 dark:text-gray-300 mb-4"
            >
              Upload Subtitle File
            </Label>
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`w-full max-w-4xl flex justify-center px-8 pt-6 pb-8 border-2 ${
                isDragging
                  ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30"
                  : "border-gray-300 dark:border-gray-600"
              } border-dashed rounded-xl transition-colors duration-200`}
            >
              <div className="space-y-3 text-center">
                <Upload
                  className={`mx-auto h-20 w-20 ${
                    isDragging ? "text-indigo-500" : "text-gray-400"
                  } transition-colors duration-200`}
                />
                <div className="flex text-xl text-gray-600 dark:text-gray-400">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer bg-white dark:bg-gray-800 rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                  >
                    <span>Upload a file</span>
                    <Input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      onChange={handleFileUpload}
                      accept=".srt,.vtt,.sub"
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-lg text-gray-500 dark:text-gray-400">
                  SRT, VTT, or SUB up to 10MB
                </p>
              </div>
            </div>
          </div>

          <div
            ref={translationSectionRef}
            className="transition-opacity duration-500 ease-in-out opacity-0 animate-fade-in"
          >
            <div className="flex flex-col md:flex-row justify-center items-center space-y-4 md:space-y-0 md:space-x-8">
              <div className="w-full md:w-2/5 max-w-xl">
                <Label
                  htmlFor="source-language"
                  className="text-xl font-medium text-gray-700 dark:text-gray-300"
                >
                  Source Language
                </Label>
                <Select
                  value={sourceLanguage}
                  onValueChange={setSourceLanguage}
                >
                  <SelectTrigger className="w-full mt-2">
                    <SelectValue placeholder="Select a language" />
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
              <Button
                variant="outline"
                size="icon"
                onClick={handleSwapLanguages}
                className="w-16 h-16 rounded-full"
              >
                <ArrowRightLeft className="h-8 w-8" />
              </Button>
              <div className="w-full md:w-2/5 max-w-xl">
                <Label
                  htmlFor="target-language"
                  className="text-xl font-medium text-gray-700 dark:text-gray-300"
                >
                  Target Language
                </Label>
                <Select
                  value={targetLanguage}
                  onValueChange={setTargetLanguage}
                >
                  <SelectTrigger className="w-full mt-2">
                    <SelectValue placeholder="Select a language" />
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
            </div>

            <div className="flex justify-center mt-8">
              <div className="w-full md:w-2/5 max-w-xl">
                <Label
                  htmlFor="ai-model"
                  className="text-xl font-medium text-gray-700 dark:text-gray-300"
                >
                  AI Model
                </Label>
                <AIModelSelector
                  selectedModel={selectedModel}
                  onModelChange={onModelChange}
                />
              </div>
            </div>

            <div className="flex justify-center mt-8">
              <SubtitleDisplayComponent
                inputSubtitles={inputSubtitles}
                translatedSubtitles={translatedSubtitles}
                onClearInput={() => {
                  setInputSubtitles("");
                  setUniqueFilename("");
                }}
                onClearOutput={clearTranslation}
              />
            </div>

            <div className="flex justify-center space-x-8 mt-8">
              <Button
                onClick={handleTranslate}
                disabled={!uniqueFilename || !targetLanguage || isProcessing}
                className="text-xl px-10 py-6"
              >
                <Globe className="mr-2 h-7 w-7" />
                {isProcessing ? "Translating..." : "Translate"}
              </Button>
              <Button
                onClick={handleDownload}
                disabled={!outputFileName}
                className="text-xl px-10 py-6"
              >
                <Download className="mr-2 h-7 w-7" /> Download
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
