"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { teacherApi, ClassOut } from "@/lib/api";
import { getToken, clearToken } from "@/lib/auth";
import { Plus, LogOut, Copy } from "lucide-react";

export default function TeacherDashboardPage() {
  const router = useRouter();
  const [classes, setClasses] = useState<ClassOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [newClassName, setNewClassName] = useState("");
  const [creating, setCreating] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [copied, setCopied] = useState<number | null>(null);

  const token = typeof window !== "undefined" ? getToken() : null;

  useEffect(() => {
    if (!token) {
      router.push("/teacher/login");
      return;
    }
    teacherApi
      .listClasses(token)
      .then(setClasses)
      .catch(() => router.push("/teacher/login"))
      .finally(() => setLoading(false));
  }, [token, router]);

  const handleCreateClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newClassName.trim() || !token) return;
    setCreating(true);
    try {
      const cls = await teacherApi.createClass(newClassName.trim(), token);
      setClasses((prev) => [cls, ...prev]);
      setNewClassName("");
      setShowCreate(false);
    } finally {
      setCreating(false);
    }
  };

  const copyCode = (cls: ClassOut) => {
    navigator.clipboard.writeText(cls.join_code);
    setCopied(cls.id);
    setTimeout(() => setCopied(null), 2000);
  };

  const handleLogout = () => {
    clearToken();
    router.push("/teacher/login");
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <p className="text-indigo-700">Loading dashboard...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-indigo-900">My Classes</h1>
          <div className="flex gap-2">
            <Button onClick={() => setShowCreate(!showCreate)} size="sm">
              <Plus className="h-4 w-4 mr-1" /> New Class
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {showCreate && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Create New Class</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateClass} className="flex gap-2">
                <Input
                  placeholder="Class name (e.g. Algebra 1 - Period 3)"
                  value={newClassName}
                  onChange={(e) => setNewClassName(e.target.value)}
                  autoFocus
                />
                <Button type="submit" disabled={creating || !newClassName.trim()}>
                  {creating ? "Creating..." : "Create"}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {classes.length === 0 && (
          <p className="text-gray-500">No classes yet. Create one to get started.</p>
        )}

        <div className="grid gap-4">
          {classes.map((cls) => (
            <Card key={cls.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-indigo-800">{cls.name}</CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="secondary"
                      className="font-mono text-sm cursor-pointer"
                      onClick={() => copyCode(cls)}
                    >
                      {cls.join_code}
                      <Copy className="h-3 w-3 ml-1" />
                    </Badge>
                    {copied === cls.id && (
                      <span className="text-xs text-green-600">Copied!</span>
                    )}
                  </div>
                </div>
                <CardDescription>
                  Created {new Date(cls.created_at).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Link href={`/teacher/class/${cls.id}`}>
                  <Button variant="outline" size="sm">
                    View Assignments &amp; Analytics
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </main>
  );
}
