"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function DashboardPage() {
  const { user } = useAuth();
  const [alignments, setAlignments] = useState<any[]>([]);
  const [resumes, setResumes] = useState<any[]>([]);

  useEffect(() => {
    api.getAlignments().then(setAlignments).catch(() => {});
    api.getResumes().then(setResumes).catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back, {user?.email}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Resumes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{resumes.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Alignments</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{alignments.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Match</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {alignments.length > 0
                ? Math.round(alignments.reduce((a: number, al: any) => a + al.overall_match_score, 0) / alignments.length)
                : "--"}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Recent Alignments</h2>
          <Link href="/jobs">
            <Button variant="outline" size="sm">Search Jobs</Button>
          </Link>
        </div>
        {alignments.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              <p>No alignments yet. Upload a resume and search for jobs to get started.</p>
              <div className="mt-4 flex justify-center gap-3">
                <Link href="/resumes">
                  <Button size="sm">Upload Resume</Button>
                </Link>
                <Link href="/jobs">
                  <Button variant="outline" size="sm">Search Jobs</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {alignments.slice(0, 5).map((al: any) => (
              <Link key={al.id} href={`/alignments/${al.id}`}>
                <Card className="transition-colors hover:bg-accent/50">
                  <CardContent className="flex items-center justify-between py-4">
                    <div>
                      <p className="font-medium">Alignment #{al.id.slice(0, 8)}</p>
                      <p className="text-sm text-muted-foreground">
                        Score: {al.overall_match_score}% | Status: {al.saved_status}
                      </p>
                    </div>
                    <Badge variant={al.overall_match_score >= 70 ? "default" : "secondary"}>
                      {al.overall_match_score}%
                    </Badge>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
