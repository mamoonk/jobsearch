"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface CoverLetterPreviewProps {
  coverLetter: string | null;
  onGenerate: () => Promise<void>;
  generating: boolean;
}

export function CoverLetterPreview({ coverLetter, onGenerate, generating }: CoverLetterPreviewProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!coverLetter) return;
    await navigator.clipboard.writeText(coverLetter);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleDownload() {
    if (!coverLetter) return;
    const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
      body { font-family: 'Georgia', serif; max-width: 600px; margin: 40px auto; padding: 20px; line-height: 1.6; font-size: 14px; }
    </style></head><body><p>${coverLetter.replace(/\n/g, "</p><p>")}</p></body></html>`;
    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "cover-letter.html";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Cover Letter</h3>
        <div className="flex gap-2">
          {coverLetter && (
            <>
              <Button variant="outline" size="sm" onClick={handleDownload}>
                Download
              </Button>
              <Button variant="outline" size="sm" onClick={handleCopy}>
                {copied ? "Copied!" : "Copy"}
              </Button>
            </>
          )}
          <Button size="sm" onClick={onGenerate} disabled={generating}>
            {generating ? "Generating..." : coverLetter ? "Regenerate" : "Generate"}
          </Button>
        </div>
      </div>
      {coverLetter ? (
        <Card>
          <CardContent className="whitespace-pre-wrap py-4 text-sm leading-relaxed">
            {coverLetter}
          </CardContent>
        </Card>
      ) : (
        <p className="text-sm text-muted-foreground">
          Generate a tailored cover letter based on your alignment analysis.
        </p>
      )}
    </div>
  );
}
