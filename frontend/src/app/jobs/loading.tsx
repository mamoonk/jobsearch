import { LoadingSpinner } from "@/components/LoadingSpinner";

export default function JobsLoading() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <LoadingSpinner size="lg" />
    </div>
  );
}
