const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (fetchOptions.headers) {
    const incoming = fetchOptions.headers;
    if (incoming instanceof Headers) {
      incoming.forEach((value, key) => { headers[key] = value; });
    } else if (Array.isArray(incoming)) {
      incoming.forEach(([key, value]) => { headers[key] = value; });
    } else {
      Object.assign(headers, incoming as Record<string, string>);
    }
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...fetchOptions,
    headers,
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error ${response.status}: ${errorText}`);
  }
  return response.json() as Promise<T>;
}

// Types
export interface ClassOut {
  id: number;
  name: string;
  join_code: string;
  teacher_id: number;
  created_at: string;
}

export interface AssignmentPolicy {
  answer_mode: "NO_ANSWER" | "ALLOW_AFTER_MASTERY" | "ALLOW";
  hint_ceiling: number;
  attempt_required: boolean;
  show_similar_example: boolean;
}

export interface AssignmentOut {
  id: number;
  title: string;
  description: string;
  class_id: number;
  policy: AssignmentPolicy;
  created_at: string;
}

export interface ProblemOut {
  id: number;
  assignment_id: number;
  problem_text: string;
  skill_tags: string[];
  order_index: number;
  created_at: string;
}

export interface TutorTelemetry {
  intent: string;
  skill_tags: string[];
  stuck_step: number;
  hint_level_served: number;
  misconception_code: string | null;
  policy_violation_prevented: boolean;
}

export interface TutorResponse {
  student_message: string;
  check_question: string;
  next_action: string;
  telemetry: TutorTelemetry;
}

export interface AnalyticsOut {
  session_count: number;
  active_student_count: number;
  avg_hint_level: number;
  top_intent_types: Record<string, number>;
  top_question_clusters: Array<{ keyword: string; count: number }>;
  most_common_stuck_step: number | null;
  policy_violations_prevented: number;
}

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    apiFetch<{ access_token: string; token_type: string }>("/auth/teacher/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: (token: string) => apiFetch<{ id: number; email: string }>("/auth/me", { token }),
};

// Teacher API
export const teacherApi = {
  createClass: (name: string, token: string) =>
    apiFetch<ClassOut>("/classes", {
      method: "POST",
      body: JSON.stringify({ name }),
      token,
    }),
  listClasses: (token: string) => apiFetch<ClassOut[]>("/classes", { token }),
  createAssignment: (
    classId: number,
    data: { title: string; description: string; policy: AssignmentPolicy },
    token: string
  ) =>
    apiFetch<AssignmentOut>(`/classes/${classId}/assignments`, {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
  listAssignments: (classId: number, token: string) =>
    apiFetch<AssignmentOut[]>(`/classes/${classId}/assignments`, { token }),
  createProblem: (
    assignmentId: number,
    data: { problem_text: string; skill_tags: string[] },
    token: string
  ) =>
    apiFetch<ProblemOut>(`/assignments/${assignmentId}/problems`, {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
  listProblems: (assignmentId: number, token: string) =>
    apiFetch<ProblemOut[]>(`/assignments/${assignmentId}/problems`, { token }),
  getAnalytics: (classId: number, assignmentId: number, token: string) =>
    apiFetch<AnalyticsOut>(`/analytics/classes/${classId}/assignments/${assignmentId}`, { token }),
};

// Student API
export const studentApi = {
  join: (classCode: string, studentAnonId: string) =>
    apiFetch<{ id: number; anon_id: string; class_id: number; joined_at: string }>(
      "/student/join",
      {
        method: "POST",
        body: JSON.stringify({ classCode, studentAnonId }),
      }
    ),
  listAssignments: (classCode: string) =>
    apiFetch<AssignmentOut[]>(`/student/classes/${classCode}/assignments`),
  listProblems: (assignmentId: number) =>
    apiFetch<ProblemOut[]>(`/assignments/${assignmentId}/problems`),
};

// Tutor API
export interface ConversationMessage {
  role: "student" | "assistant";
  content: string;
}

export const tutorApi = {
  next: (
    studentAnonId: string,
    classCode: string,
    assignmentId: number,
    problemId: number,
    conversationHistory: ConversationMessage[],
    studentMessage: string
  ) =>
    apiFetch<TutorResponse>("/tutor/next", {
      method: "POST",
      body: JSON.stringify({
        studentAnonId,
        classCode,
        assignmentId,
        problemId,
        conversationHistory,
        studentMessage,
      }),
    }),
};
