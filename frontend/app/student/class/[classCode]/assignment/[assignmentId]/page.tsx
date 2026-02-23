"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { studentApi, ProblemOut } from "@/lib/api";

export default function AssignmentPage() {
  const params = useParams<{ classCode: string; assignmentId: string }>();
  const { classCode, assignmentId } = params;
  const [problems, setProblems] = useState<ProblemOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!assignmentId) return;
    studentApi
      .listProblems(Number(assignmentId))
      .then(setProblems)
      .catch(() => setError("Could not load problems."))
      .finally(() => setLoading(false));
  }, [assignmentId]);

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <p className="text-indigo-700">Loading problems...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <Link
            href={`/student/class/${classCode}`}
            className="text-indigo-600 hover:underline text-sm"
          >
            ← Back to assignments
          </Link>
          <h1 className="text-3xl font-bold text-indigo-900 mt-2">Choose a Problem</h1>
        </div>
        {error && <p className="text-red-600">{error}</p>}
        {problems.length === 0 && !error && (
          <p className="text-gray-500">No problems available yet.</p>
        )}
        <div className="grid gap-4">
          {problems.map((problem, idx) => (
            <Link
              key={problem.id}
              href={`/student/class/${classCode}/assignment/${assignmentId}/problem/${problem.id}`}
            >
              <Card className="hover:shadow-lg transition-shadow cursor-pointer hover:border-indigo-300">
                <CardHeader>
                  <CardTitle className="text-indigo-800 text-lg">
                    Problem {idx + 1}
                  </CardTitle>
                  <CardDescription className="text-base font-mono">
                    {problem.problem_text}
                  </CardDescription>
                </CardHeader>
                {problem.skill_tags.length > 0 && (
                  <CardContent className="flex gap-2 flex-wrap">
                    {problem.skill_tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </CardContent>
                )}
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
