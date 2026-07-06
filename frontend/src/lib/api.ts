const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  constructor() {
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("token");
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("token", token);
      } else {
        localStorage.removeItem("token");
      }
    }
  }

  getToken() {
    return this.token;
  }

  private async request<T>(
    path: string,
    method: string = "GET",
    body?: unknown,
    extraHeaders?: Record<string, string>
  ): Promise<T> {
    const headers: Record<string, string> = {};
    if (!(body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }
    if (extraHeaders) {
      Object.assign(headers, extraHeaders);
    }

    const res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body instanceof FormData ? body as any : body ? JSON.stringify(body) : undefined,
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Request failed");
    }

    if (res.status === 204) return undefined as T;
    return res.json();
  }

  // Auth
  register(email: string, password: string) {
    return this.request<{ access_token: string; token_type: string }>(
      "/api/v1/auth/register", "POST", { email, password }
    );
  }

  login(email: string, password: string) {
    return this.request<{ access_token: string; token_type: string }>(
      "/api/v1/auth/login", "POST", { email, password }
    );
  }

  getMe() {
    return this.request<{ id: string; email: string }>("/api/v1/auth/me");
  }

  // Resumes
  uploadResume(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return this.request<any>("/api/v1/resumes/upload", "POST", formData);
  }

  getResumes() {
    return this.request<any[]>("/api/v1/resumes/");
  }

  getResume(id: string) {
    return this.request<any>(`/api/v1/resumes/${id}`);
  }

  deleteResume(id: string) {
    return this.request<void>(`/api/v1/resumes/${id}`, "DELETE");
  }

  // Jobs & Search
  searchJobs(keyword: string, location: string) {
    return this.request<any[]>(
      `/api/v1/search/jobs?keyword=${encodeURIComponent(keyword)}&location=${encodeURIComponent(location)}`,
      "POST"
    );
  }

  autocompleteLocation(q: string) {
    return this.request<any[]>(`/api/v1/search/autocomplete?q=${encodeURIComponent(q)}`);
  }

  getJobs(page = 0, limit = 20) {
    return this.request<any[]>(`/api/v1/jobs/?page=${page}&limit=${limit}`);
  }

  getJob(id: string) {
    return this.request<any>(`/api/v1/jobs/${id}`);
  }

  // Alignments
  createAlignment(jobId: string, resumeId: string) {
    return this.request<any>("/api/v1/alignments/", "POST", {
      job_id: jobId,
      resume_id: resumeId,
    });
  }

  getAlignments() {
    return this.request<any[]>("/api/v1/alignments/");
  }

  getAlignment(id: string) {
    return this.request<any>(`/api/v1/alignments/${id}`);
  }

  updateAlignmentStatus(id: string, status: string) {
    return this.request<any>(
      `/api/v1/alignments/${id}/status?status_value=${encodeURIComponent(status)}`,
      "PATCH"
    );
  }

  // Cover Letter
  generateCoverLetter(alignmentId: string) {
    return this.request<{ cover_letter: string }>(
      `/api/v1/cover-letters/${alignmentId}`, "POST"
    );
  }

  // Interview Prep
  generateInterviewPrep(alignmentId: string) {
    return this.request<{ questions: any[] }>(
      `/api/v1/interview-prep/${alignmentId}`, "POST"
    );
  }
}

export const api = new ApiClient();
