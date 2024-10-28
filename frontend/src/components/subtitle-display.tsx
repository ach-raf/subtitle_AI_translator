"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { X, Download, Edit2 } from "lucide-react";

interface SubtitleEntry {
  index: number;
  timeCode: string;
  text: string;
}

function parseSubtitles(subtitles: string): SubtitleEntry[] {
  if (!subtitles.trim()) return [];
  const normalizedSubtitles = subtitles.replace(/\r\n/g, "\n");
  const pattern =
    /(\d+)\n(\d{2}:\d{2}:\d{2},\d{2,3} --> \d{2}:\d{2}:\d{2},\d{2,3})\n([\s\S]*?)(?=\n{2}|\n*$)/g;
  const entries: SubtitleEntry[] = [];
  let match;
  while ((match = pattern.exec(normalizedSubtitles)) !== null) {
    const index = parseInt(match[1], 10);
    const timeCode = match[2];
    const text = match[3].trim().replace(/<\/?i>/g, "");
    entries.push({ index, timeCode, text });
  }
  return entries;
}

function formatSRT(entries: SubtitleEntry[]): string {
  return entries
    .map((entry) => `${entry.index}\n${entry.timeCode}\n${entry.text}\n`)
    .join("\n");
}

export default function SubtitleDisplayComponent({
  inputSubtitles,
  translatedSubtitles,
  onClearInput,
  onClearOutput,
}: {
  inputSubtitles: string;
  translatedSubtitles: string;
  onClearInput: () => void;
  onClearOutput: () => void;
}) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [sourceEntries, setSourceEntries] = useState<SubtitleEntry[]>([]);
  const [targetEntries, setTargetEntries] = useState<SubtitleEntry[]>([]);
  const sourceScrollRef = useRef<HTMLDivElement>(null);
  const targetScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSourceEntries(parseSubtitles(inputSubtitles));
  }, [inputSubtitles]);

  useEffect(() => {
    setTargetEntries(parseSubtitles(translatedSubtitles));
  }, [translatedSubtitles]);

  const handleRowSelect = useCallback(
    (index: number, scrollRef: React.RefObject<HTMLDivElement>) => {
      setSelectedIndex(index);

      if (scrollRef.current) {
        const scrollContainer = scrollRef.current.querySelector(
          "[data-radix-scroll-area-viewport]"
        );
        const selectedRow = scrollRef.current.querySelector(
          `[data-index="${index}"]`
        );
        if (scrollContainer && selectedRow) {
          const { offsetTop } = selectedRow as HTMLElement;
          scrollContainer.scrollTo({
            top: offsetTop,
            behavior: "smooth",
          });
        }
      }
    },
    []
  );

  const handleTextEdit = useCallback(
    (
      index: number,
      newText: string,
      setEntries: React.Dispatch<React.SetStateAction<SubtitleEntry[]>>
    ) => {
      setEntries((prevEntries) =>
        prevEntries.map((entry) =>
          entry.index === index ? { ...entry, text: newText } : entry
        )
      );
    },
    []
  );

  const handleDownload = useCallback(
    (entries: SubtitleEntry[], fileName: string) => {
      const content = formatSRT(entries);
      const blob = new Blob([content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
    []
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div>
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-medium">Input Subtitles</h3>
          <div className="space-x-2">
            {sourceEntries.length > 0 && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    handleDownload(sourceEntries, "source_subtitles.srt")
                  }
                  className="text-gray-500 hover:text-gray-700"
                >
                  <Download className="h-4 w-4 mr-1" /> Download
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClearInput}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="h-4 w-4 mr-1" /> Clear Input
                </Button>
              </>
            )}
          </div>
        </div>
        <SubtitleTable
          entries={sourceEntries}
          selectedIndex={selectedIndex}
          onSelectRow={(index) => {
            handleRowSelect(index, sourceScrollRef);
            handleRowSelect(index, targetScrollRef);
          }}
          onTextEdit={(index, newText) =>
            handleTextEdit(index, newText, setSourceEntries)
          }
          scrollRef={sourceScrollRef}
        />
      </div>
      <div>
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-medium">Translated Subtitles</h3>
          <div className="space-x-2">
            {targetEntries.length > 0 && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    handleDownload(targetEntries, "translated_subtitles.srt")
                  }
                  className="text-gray-500 hover:text-gray-700"
                >
                  <Download className="h-4 w-4 mr-1" /> Download
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClearOutput}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="h-4 w-4 mr-1" /> Clear Translation
                </Button>
              </>
            )}
          </div>
        </div>
        <SubtitleTable
          entries={targetEntries}
          selectedIndex={selectedIndex}
          onSelectRow={(index) => {
            handleRowSelect(index, sourceScrollRef);
            handleRowSelect(index, targetScrollRef);
          }}
          onTextEdit={(index, newText) =>
            handleTextEdit(index, newText, setTargetEntries)
          }
          scrollRef={targetScrollRef}
        />
      </div>
    </div>
  );
}

function SubtitleTable({
  entries,
  selectedIndex,
  onSelectRow,
  onTextEdit,
  scrollRef,
}: {
  entries: SubtitleEntry[];
  selectedIndex: number | null;
  onSelectRow: (index: number) => void;
  onTextEdit: (index: number, newText: string) => void;
  scrollRef: React.RefObject<HTMLDivElement>;
}) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editText, setEditText] = useState("");

  const handleEditClick = (index: number, text: string) => {
    setEditingIndex(index);
    setEditText(text);
  };

  const handleEditSubmit = (index: number) => {
    onTextEdit(index, editText);
    setEditingIndex(null);
  };

  return (
    <ScrollArea className="h-[480px] border rounded-md" ref={scrollRef}>
      <Table className="min-w-[600px]">
        <TableHeader>
          <TableRow>
            <TableHead className="w-16 sticky top-0 bg-background">
              Index
            </TableHead>
            <TableHead className="w-40 sticky top-0 bg-background">
              Time Code
            </TableHead>
            <TableHead className="sticky top-0 bg-background">Text</TableHead>
            <TableHead className="w-20 sticky top-0 bg-background">
              Edit
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {entries.length > 0 ? (
            entries.map((entry) => (
              <TableRow
                key={entry.index}
                data-index={entry.index}
                className={`transition-colors ${
                  selectedIndex === entry.index
                    ? "bg-muted"
                    : "hover:bg-muted/50"
                }`}
                onClick={() => onSelectRow(entry.index)}
              >
                <TableCell className="font-medium truncate">
                  {entry.index}
                </TableCell>
                <TableCell className="font-mono text-sm truncate">
                  {entry.timeCode}
                </TableCell>
                <TableCell className="truncate">
                  {editingIndex === entry.index ? (
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        handleEditSubmit(entry.index);
                      }}
                    >
                      <Input
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        onBlur={() => handleEditSubmit(entry.index)}
                        autoFocus
                      />
                    </form>
                  ) : (
                    entry.text
                  )}
                </TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEditClick(entry.index, entry.text);
                    }}
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={4} className="text-center py-4 text-gray-500">
                No subtitles available
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </ScrollArea>
  );
}
