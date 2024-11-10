import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { AIModel } from "@/types/ai-model";

interface AIModelSelectorProps {
  selectedModel: AIModel;
  onModelChange: (model: AIModel) => void;
}

export function AIModelSelector({
  selectedModel,
  onModelChange,
}: AIModelSelectorProps) {
  return (
    <div className="flex items-center space-x-2">
      <label htmlFor="ai-model-select" className="text-sm font-medium">
        AI Model:
      </label>
      <Select
        value={selectedModel}
        onValueChange={(value) => onModelChange(value as AIModel)}
      >
        <SelectTrigger id="ai-model-select" className="w-[180px]">
          <SelectValue placeholder="Select AI Model" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="opus">OPUS</SelectItem>
          <SelectItem value="m2m100">M2M100</SelectItem>
          <SelectItem value="nllb">NLLB</SelectItem>
          <SelectItem value="madlad">MADLAD</SelectItem>
          <SelectItem value="seamless">SEAMLESS</SelectItem>
          <SelectItem value="darija">Moroccan Darija</SelectItem>
          <SelectItem value="faseeh">Faseeh</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
