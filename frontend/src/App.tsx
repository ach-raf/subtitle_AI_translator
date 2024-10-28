import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TextTranslationComponent } from "./components/text-translation";
import { SubtitleServiceComponent } from "./components/subtitle-service";
import { AIModelSelector, AIModel } from "./components/ai-model-selector";

export default function App() {
  const [selectedModel, setSelectedModel] = useState<AIModel>("opus");

  return (
    <div className="container mx-auto p-4 max-w-[1920px]">
      <h1 className="text-4xl font-bold text-center mb-8">
        Translation Services
      </h1>
      <div className="flex justify-end mb-4">
        <AIModelSelector
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
        />
      </div>
      <Tabs defaultValue="text" className="w-full">
        <div className="flex justify-center mb-6">
          <TabsList className="grid w-full max-w-2xl grid-cols-2">
            <TabsTrigger value="text" className="text-lg py-3">
              Text Translation
            </TabsTrigger>
            <TabsTrigger value="subtitle" className="text-lg py-3">
              Subtitle Processing
            </TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="text">
          <div className="mt-6">
            <TextTranslationComponent
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
            />
          </div>
        </TabsContent>
        <TabsContent value="subtitle">
          <div className="mt-6">
            <SubtitleServiceComponent
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
