"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Question {
  question_type: string;
  targeted_skill: string;
  interview_question: string;
  strategic_intent: string;
  optimal_response_script: string;
}

interface InterviewPrepCardsProps {
  questions: Question[] | null;
  onGenerate: () => Promise<void>;
  generating: boolean;
}

export function InterviewPrepCards({ questions, onGenerate, generating }: InterviewPrepCardsProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Interview Preparation</h3>
        <Button size="sm" onClick={onGenerate} disabled={generating}>
          {generating ? "Generating..." : questions ? "Regenerate" : "Generate"}
        </Button>
      </div>
      {questions && questions.length > 0 ? (
        <div className="space-y-3">
          {questions.map((q, i) => (
            <Card
              key={i}
              className="cursor-pointer transition-colors hover:bg-accent/30"
              onClick={() => setOpenIndex(openIndex === i ? null : i)}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-sm">{q.interview_question}</CardTitle>
                  </div>
                  <Badge variant="outline" className="ml-2 shrink-0">
                    {q.question_type === "Technical Defense Vector" ? "Technical" : "Behavioral"}
                  </Badge>
                </div>
              </CardHeader>
              {openIndex === i && (
                <CardContent className="space-y-3 text-sm">
                  <div>
                    <span className="font-medium text-muted-foreground">Targeted Skill: </span>
                    <span>{q.targeted_skill}</span>
                  </div>
                  <div>
                    <span className="font-medium text-muted-foreground">Strategic Intent: </span>
                    <span>{q.strategic_intent}</span>
                  </div>
                  <div>
                    <span className="font-medium text-muted-foreground">Optimal Response: </span>
                    <p className="mt-1 whitespace-pre-wrap text-muted-foreground">
                      {q.optimal_response_script}
                    </p>
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          Generate interview prep questions tailored to your alignment gaps.
        </p>
      )}
    </div>
  );
}
