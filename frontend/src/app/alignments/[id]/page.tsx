"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScoreGauge } from "@/components/alignment/ScoreGauge";
import { GapAnalysisView } from "@/components/alignment/GapAnalysis";
import { CoverLetterPreview } from "@/components/alignment/CoverLetterPreview";
import { InterviewPrepCards } from "@/components/alignment/InterviewPrepCards";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function AlignmentPage() {
  const params = useParams();
  const [alignment, setAlignment] = useState<any>(null);
  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generatingCL, setGeneratingCL] = useState(false);
  const [generatingIP, setGeneratingIP] = useState(false);

  useEffect(() => {
    const aid = params.id as string;
    api.getAlignment(aid).then(async (al) => {
      setAlignment(al);
      const j = await api.getJob(al.job_id);
      setJob(j);
    }).finally(() => setLoading(false));
  }, [params.id]);

  async function handleGenerateCL() {
    if (!alignment) return;
    setGeneratingCL(true);
    try {
      const res = await api.generateCoverLetter(alignment.id);
      setAlignment({ ...alignment, generated_cover_letter: res.cover_letter });
    } catch (err: any) {
      alert(err.message);
    } finally {
      setGeneratingCL(false);
    }
  }

  async function handleGenerateIP() {
    if (!alignment) return;
    setGeneratingIP(true);
    try {
      const res = await api.generateInterviewPrep(alignment.id);
      setAlignment({ ...alignment, interview_prep_json: res.questions });
    } catch (err: any) {
      alert(err.message);
    } finally {
      setGeneratingIP(false);
    }
  }

  async function handleStatusChange(status: string) {
    if (!alignment) return;
    await api.updateAlignmentStatus(alignment.id, status);
    setAlignment({ ...alignment, saved_status: status });
  }

  if (loading) return <div className="p-6 text-center text-muted-foreground">Loading...</div>;
  if (!alignment || !job) return <div className="p-6 text-center text-muted-foreground">Alignment not found</div>;

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground">
            &larr; Dashboard
          </Link>
          <h1 className="text-2xl font-bold">{job.title}</h1>
          <p className="text-muted-foreground">{job.company_name}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge>{alignment.saved_status}</Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleStatusChange("applied")}
            disabled={alignment.saved_status === "applied"}
          >
            Mark Applied
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Match Scores</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <ScoreGauge label="Overall Match" score={alignment.overall_match_score} />
            <ScoreGauge label="Keyword Overlap" score={alignment.keyword_score} />
            <ScoreGauge label="Experience Fit" score={alignment.experience_score} />
            <ScoreGauge label="Semantic Similarity" score={alignment.semantic_score} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Gap Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <GapAnalysisView gapLog={alignment.gap_analysis_json} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Job Description</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap text-sm text-muted-foreground">
            {job.description}
          </p>
          <div className="mt-4">
            <a
              href={job.apply_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary underline-offset-4 hover:underline"
            >
              Apply on {job.company_name}&apos;s website &rarr;
            </a>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="cover-letter">
        <TabsList>
          <TabsTrigger value="cover-letter">Cover Letter</TabsTrigger>
          <TabsTrigger value="interview-prep">Interview Prep</TabsTrigger>
        </TabsList>
        <TabsContent value="cover-letter" className="mt-4">
          <CoverLetterPreview
            coverLetter={alignment.generated_cover_letter}
            onGenerate={handleGenerateCL}
            generating={generatingCL}
          />
        </TabsContent>
        <TabsContent value="interview-prep" className="mt-4">
          <InterviewPrepCards
            questions={alignment.interview_prep_json}
            onGenerate={handleGenerateIP}
            generating={generatingIP}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
