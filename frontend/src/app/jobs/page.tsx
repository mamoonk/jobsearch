"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface Job {
  id: string;
  title: string;
  company_name: string;
  city?: string;
  state?: string;
  country?: string;
  workplace_modality?: string;
  employment_type?: string;
  salary_min?: number;
  salary_max?: number;
}

export default function JobsPage() {
  const router = useRouter();
  const [keyword, setKeyword] = useState("");
  const [location, setLocation] = useState("");
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [searching, setSearching] = useState(false);
  const [resumes, setResumes] = useState<any[]>([]);

  useEffect(() => {
    api.getResumes().then(setResumes).catch(() => {});
  }, []);

  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.length < 2) {
      setSuggestions([]);
      return;
    }
    try {
      const results = await api.autocompleteLocation(q);
      setSuggestions(results);
    } catch {
      setSuggestions([]);
    }
  }, []);

  async function handleSearch() {
    if (!keyword || !location) return;
    setSearching(true);
    try {
      const results = await api.searchJobs(keyword, location);
      setJobs(results);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSearching(false);
    }
  }

  async function handleAlign(jobId: string) {
    const primary = resumes.find((r: any) => r.is_primary) || resumes[0];
    if (!primary) {
      alert("Upload a resume first");
      router.push("/resumes");
      return;
    }
    try {
      const alignment = await api.createAlignment(jobId, primary.id);
      router.push(`/alignments/${alignment.id}`);
    } catch (err: any) {
      alert(err.message);
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <h1 className="text-2xl font-bold">Search Jobs</h1>

      <div className="flex gap-3">
        <div className="flex-1">
          <Input
            placeholder="Job title, keyword, or company"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
        </div>
        <div className="relative flex-1">
          <Input
            placeholder="City, state, or zip code"
            value={location}
            onChange={(e) => {
              setLocation(e.target.value);
              fetchSuggestions(e.target.value);
            }}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          {suggestions.length > 0 && (
            <Card className="absolute z-10 mt-1 w-full shadow-lg">
              <CardContent className="p-1">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-accent rounded-sm"
                    onClick={() => {
                      setLocation(s.search_query);
                      setSuggestions([]);
                    }}
                  >
                    {s.search_query}
                  </button>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
        <Button onClick={handleSearch} disabled={searching}>
          {searching ? "Searching..." : "Search"}
        </Button>
      </div>

      <div className="space-y-3">
        {jobs.map((job) => (
          <Card key={job.id} className="transition-colors hover:bg-accent/30">
            <CardContent className="flex items-start justify-between py-4">
              <div className="flex-1">
                <h3 className="font-semibold">{job.title}</h3>
                <p className="text-sm text-muted-foreground">{job.company_name}</p>
                <div className="mt-1 flex flex-wrap gap-2 text-xs text-muted-foreground">
                  {job.city && <span>{[job.city, job.state, job.country].filter(Boolean).join(", ")}</span>}
                  {job.workplace_modality && <Badge variant="outline">{job.workplace_modality}</Badge>}
                  {job.employment_type && <Badge variant="outline">{job.employment_type}</Badge>}
                  {(job.salary_min || job.salary_max) && (
                    <span>
                      {job.salary_min ? `$${job.salary_min.toLocaleString()}` : ""}
                      {job.salary_min && job.salary_max ? " - " : ""}
                      {job.salary_max ? `$${job.salary_max.toLocaleString()}` : ""}
                    </span>
                  )}
                </div>
              </div>
              <Button size="sm" onClick={() => handleAlign(job.id)}>
                Align
              </Button>
            </CardContent>
          </Card>
        ))}
        {jobs.length === 0 && !searching && (
          <p className="py-12 text-center text-muted-foreground">
            Enter a keyword and location to search for jobs.
          </p>
        )}
      </div>
    </div>
  );
}
