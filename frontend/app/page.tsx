import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center space-y-8">
        <div>
          <h1 className="text-4xl font-bold text-indigo-900 mb-2">Figure It Out</h1>
          <p className="text-lg text-indigo-700">
            Integrity-first AI tutor · Your thinking, guided
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="text-indigo-800">I&apos;m a Student</CardTitle>
              <CardDescription>Join your class and start learning</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/student/join">
                <Button className="w-full" size="lg">
                  Join a Class
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="text-indigo-800">I&apos;m a Teacher</CardTitle>
              <CardDescription>Manage classes and view analytics</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/teacher/login">
                <Button variant="outline" className="w-full" size="lg">
                  Teacher Login
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        <p className="text-sm text-gray-500">
          No account needed for students · Privacy-first · Works on Chromebooks
        </p>
      </div>
    </main>
  );
}
