"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function ResumeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [resume, setResume] = useState<any>(null);

  useEffect(() => {
    api.getResume(params.id as string).then(setResume).catch(() => router.push("/resumes"));
  }, [params.id, router]);

  if (!resume) return <div className="p-6 text-center text-muted-foreground">Loading...</div>;

  const data = resume.structured_json;

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{data.full_name || "Resume"}</h1>
        {resume.is_primary && <Badge>Primary</Badge>}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Hard Skills</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {data.hard_skills?.length > 0
              ? data.hard_skills.map((s: string) => <Badge key={s} variant="secondary">{s}</Badge>)
              : <span className="text-sm text-muted-foreground">No skills listed</span>}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Soft Skills</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {data.soft_skills?.length > 0
              ? data.soft_skills.map((s: string) => <Badge key={s} variant="outline">{s}</Badge>)
              : <span className="text-sm text-muted-foreground">No soft skills listed</span>}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Employment History</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {data.employment_history?.length > 0
            ? data.employment_history.map((exp: any, i: number) => (
                <div key={i}>
                  <h4 className="font-medium">{exp.role_title} at {exp.company}</h4>
                  <p className="text-sm text-muted-foreground">{exp.duration_months} months</p>
                  <ul className="mt-1 list-disc pl-5 text-sm text-muted-foreground">
                    {exp.core_impact_bullets?.map((b: string, j: number) => (
                      <li key={j}>{b}</li>
                    ))}
                  </ul>
                </div>
              ))
            : <span className="text-sm text-muted-foreground">No employment history</span>}
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button variant="outline" onClick={() => router.push("/resumes")}>
          Back to Resumes
        </Button>
      </div>
    </div>
  );
}
