"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { studentApi } from "@/lib/api";
import { getOrCreateStudentId } from "@/lib/student-id";

export default function JoinPage() {
  const router = useRouter();
  const [classCode, setClassCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!classCode.trim()) return;
    setLoading(true);
    setError("");
    try {
      const studentId = getOrCreateStudentId();
      await studentApi.join(classCode.trim().toUpperCase(), studentId);
      router.push(`/student/class/${classCode.trim().toUpperCase()}`);
    } catch {
      setError("Class not found. Please check your code and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-indigo-900">Join a Class</CardTitle>
          <CardDescription>Enter the class code your teacher gave you</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleJoin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="classCode">Class Code</Label>
              <Input
                id="classCode"
                type="text"
                placeholder="e.g. DEMO01"
                value={classCode}
                onChange={(e) => setClassCode(e.target.value.toUpperCase())}
                className="text-2xl font-mono text-center tracking-widest uppercase"
                maxLength={10}
                autoFocus
                autoComplete="off"
              />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading || !classCode.trim()}>
              {loading ? "Joining..." : "Join Class"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
