"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { studentApi, AssignmentOut } from "@/lib/api";

export default function StudentClassPage() {
  const params = useParams<{ classCode: string }>();
  const classCode = params.classCode;
  const [assignments, setAssignments] = useState<AssignmentOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!classCode) return;
    studentApi
      .listAssignments(classCode)
      .then(setAssignments)
      .catch(() => setError("Could not load assignments."))
      .finally(() => setLoading(false));
  }, [classCode]);

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <p className="text-indigo-700">Loading assignments...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-indigo-900">Class {classCode}</h1>
          <p className="text-indigo-600">Choose an assignment to work on</p>
        </div>
        {error && <p className="text-red-600">{error}</p>}
        {assignments.length === 0 && !error && (
          <p className="text-gray-500">No assignments available yet.</p>
        )}
        <div className="grid gap-4">
          {assignments.map((assignment) => (
            <Link
              key={assignment.id}
              href={`/student/class/${classCode}/assignment/${assignment.id}`}
            >
              <Card className="hover:shadow-lg transition-shadow cursor-pointer hover:border-indigo-300">
                <CardHeader>
                  <CardTitle className="text-indigo-800">{assignment.title}</CardTitle>
                  {assignment.description && (
                    <CardDescription>{assignment.description}</CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <Badge variant="secondary">
                    {assignment.policy?.answer_mode === "NO_ANSWER"
                      ? "Guided Mode"
                      : "Practice Mode"}
                  </Badge>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
