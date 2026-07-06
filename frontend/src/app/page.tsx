import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center px-4 py-24 text-center">
      <h1 className="max-w-3xl text-4xl font-bold tracking-tight sm:text-5xl">
        Global Job Search, ATS Alignment & Interview Prep
      </h1>
      <p className="mt-6 max-w-2xl text-lg text-muted-foreground">
        Upload your resume, search jobs worldwide, get AI-powered match scores, generate targeted cover letters, and prepare with custom interview questions.
      </p>
      <div className="mt-10 flex gap-4">
        <Link href="/register">
          <Button size="lg">Get Started</Button>
        </Link>
        <Link href="/login">
          <Button variant="outline" size="lg">Sign In</Button>
        </Link>
      </div>
    </div>
  );
}
