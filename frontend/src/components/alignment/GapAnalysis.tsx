import { Badge } from "@/components/ui/badge";

interface GapAnalysisProps {
  gapLog: {
    detected_matching_keywords: string[];
    missing_critical_competencies: string[];
    total_candidate_months: number;
    target_required_months: number;
  };
}

export function GapAnalysisView({ gapLog }: GapAnalysisProps) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="mb-2 text-sm font-medium">Matching Keywords</h4>
        <div className="flex flex-wrap gap-1">
          {gapLog.detected_matching_keywords.length > 0 ? (
            gapLog.detected_matching_keywords.map((kw) => (
              <Badge key={kw} variant="default">{kw}</Badge>
            ))
          ) : (
            <span className="text-sm text-muted-foreground">No direct matches found</span>
          )}
        </div>
      </div>

      <div>
        <h4 className="mb-2 text-sm font-medium">Missing Competencies</h4>
        <div className="flex flex-wrap gap-1">
          {gapLog.missing_critical_competencies.length > 0 ? (
            gapLog.missing_critical_competencies.map((sk) => (
              <Badge key={sk} variant="destructive">{sk}</Badge>
            ))
          ) : (
            <span className="text-sm text-muted-foreground">No critical gaps detected</span>
          )}
        </div>
      </div>

      <div>
        <h4 className="mb-2 text-sm font-medium">Experience</h4>
        <p className="text-sm text-muted-foreground">
          {gapLog.total_candidate_months} months of experience (target: {gapLog.target_required_months} months)
        </p>
      </div>
    </div>
  );
}
