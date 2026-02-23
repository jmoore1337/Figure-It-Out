"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { teacherApi, AssignmentOut } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Plus } from "lucide-react";

export default function ClassPage() {
  const params = useParams<{ classId: string }>();
  const classId = Number(params.classId);
  const router = useRouter();
  const [assignments, setAssignments] = useState<AssignmentOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  const token = typeof window !== "undefined" ? getToken() : null;

  useEffect(() => {
    if (!token) { router.push("/teacher/login"); return; }
    teacherApi
      .listAssignments(classId, token)
      .then(setAssignments)
      .catch(() => router.push("/teacher/login"))
      .finally(() => setLoading(false));
  }, [classId, token, router]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !token) return;
    setCreating(true);
    try {
      const a = await teacherApi.createAssignment(
        classId,
        {
          title: title.trim(),
          description: description.trim(),
          policy: {
            answer_mode: "NO_ANSWER",
            hint_ceiling: 3,
            attempt_required: true,
            show_similar_example: false,
          },
        },
        token
      );
      setAssignments((prev) => [a, ...prev]);
      setTitle("");
      setDescription("");
      setShowCreate(false);
    } finally {
      setCreating(false);
    }
  };

  if (loading) return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <p className="text-indigo-700">Loading...</p>
    </main>
  );

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Link href="/teacher/dashboard" className="text-indigo-600 hover:underline text-sm">
              ← Back to Dashboard
            </Link>
            <h1 className="text-3xl font-bold text-indigo-900 mt-1">Assignments</h1>
          </div>
          <Button onClick={() => setShowCreate(!showCreate)} size="sm">
            <Plus className="h-4 w-4 mr-1" /> New Assignment
          </Button>
        </div>

        {showCreate && (
          <Card>
            <CardHeader><CardTitle className="text-lg">Create Assignment</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-3">
                <div className="space-y-1">
                  <Label>Title</Label>
                  <Input
                    placeholder="e.g. Solving Linear Equations"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    autoFocus
                  />
                </div>
                <div className="space-y-1">
                  <Label>Description (optional)</Label>
                  <Input
                    placeholder="Brief description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>
                <Button type="submit" disabled={creating || !title.trim()}>
                  {creating ? "Creating..." : "Create"}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {assignments.length === 0 && !showCreate && (
          <p className="text-gray-500">No assignments yet.</p>
        )}

        <div className="grid gap-4">
          {assignments.map((a) => (
            <Card key={a.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-indigo-800">{a.title}</CardTitle>
                    {a.description && <CardDescription>{a.description}</CardDescription>}
                  </div>
                  <Badge variant="outline">
                    {a.policy?.answer_mode === "NO_ANSWER" ? "No Answers" : a.policy?.answer_mode}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <Link href={`/teacher/class/${classId}/assignment/${a.id}`}>
                  <Button variant="outline" size="sm">View Analytics</Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </main>
  );
}
