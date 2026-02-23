"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { teacherApi, AnalyticsOut } from "@/lib/api";
import { getToken } from "@/lib/auth";

export default function AssignmentAnalyticsPage() {
  const params = useParams<{ classId: string; assignmentId: string }>();
  const classId = Number(params.classId);
  const assignmentId = Number(params.assignmentId);
  const router = useRouter();
  const [analytics, setAnalytics] = useState<AnalyticsOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const token = typeof window !== "undefined" ? getToken() : null;

  useEffect(() => {
    if (!token) { router.push("/teacher/login"); return; }
    teacherApi
      .getAnalytics(classId, assignmentId, token)
      .then(setAnalytics)
      .catch(() => setError("Could not load analytics."))
      .finally(() => setLoading(false));
  }, [classId, assignmentId, token, router]);

  if (loading) return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <p className="text-indigo-700">Loading analytics...</p>
    </main>
  );

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <Link href={`/teacher/class/${classId}`} className="text-indigo-600 hover:underline text-sm">
            ← Back to Assignments
          </Link>
          <h1 className="text-3xl font-bold text-indigo-900 mt-1">Assignment Analytics</h1>
        </div>

        {error && <p className="text-red-600">{error}</p>}

        {analytics && (
          <>
            {/* Overview Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: "Sessions", value: analytics.session_count },
                { label: "Active Students", value: analytics.active_student_count },
                { label: "Avg Hint Level", value: analytics.avg_hint_level.toFixed(1) },
                { label: "Violations Prevented", value: analytics.policy_violations_prevented },
              ].map((stat) => (
                <Card key={stat.label} className="text-center">
                  <CardContent className="pt-4">
                    <p className="text-3xl font-bold text-indigo-700">{stat.value}</p>
                    <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Most common stuck step */}
            {analytics.most_common_stuck_step !== null && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Most Common Stuck Step</CardTitle>
                </CardHeader>
                <CardContent>
                  <span className="text-2xl font-bold text-amber-600">
                    Step {analytics.most_common_stuck_step}
                  </span>
                </CardContent>
              </Card>
            )}

            {/* Intent types */}
            {Object.keys(analytics.top_intent_types).length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Top Intent Types</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2">
                  {Object.entries(analytics.top_intent_types)
                    .sort(([, a], [, b]) => b - a)
                    .map(([intent, count]) => (
                      <Badge key={intent} variant="secondary">
                        {intent.replace(/_/g, " ")}: {count}
                      </Badge>
                    ))}
                </CardContent>
              </Card>
            )}

            {/* Question clusters */}
            {analytics.top_question_clusters.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Top Question Keywords</CardTitle>
                  <CardDescription>Most common terms in student messages</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {analytics.top_question_clusters.map((cluster) => (
                      <div key={cluster.keyword} className="flex items-center gap-2">
                        <div
                          className="bg-indigo-200 rounded h-4"
                          style={{
                            width: `${Math.min(
                              (cluster.count /
                                (analytics.top_question_clusters[0]?.count || 1)) *
                                100,
                              100
                            )}%`,
                            minWidth: "8px",
                          }}
                        />
                        <span className="text-sm font-mono">{cluster.keyword}</span>
                        <span className="text-xs text-gray-400">({cluster.count})</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {analytics.session_count === 0 && (
              <Card>
                <CardContent className="pt-6 text-center text-gray-500">
                  No student sessions yet for this assignment.
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </main>
  );
}
