"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { tutorApi, studentApi, ProblemOut, ConversationMessage } from "@/lib/api";
import { getOrCreateStudentId } from "@/lib/student-id";
import { Send } from "lucide-react";

interface ChatMessage {
  role: "student" | "assistant";
  content: string;
  checkQuestion?: string;
}

export default function TutorChatPage() {
  const params = useParams<{
    classCode: string;
    assignmentId: string;
    problemId: string;
  }>();
  const { classCode, assignmentId, problemId } = params;

  const [problem, setProblem] = useState<ProblemOut | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [hintLevel, setHintLevel] = useState(0);
  const [violationPrevented, setViolationPrevented] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!assignmentId) return;
    studentApi.listProblems(Number(assignmentId)).then((problems) => {
      const p = problems.find((x) => x.id === Number(problemId));
      if (p) setProblem(p);
    });
    setMessages([
      {
        role: "assistant",
        content:
          "Hi! I'm your tutor for this problem. I won't give you the answer directly, but I'll help you figure it out. What have you tried so far, or where would you like to start?",
        checkQuestion: "What do you know about this problem?",
      },
    ]);
  }, [assignmentId, problemId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || loading) return;
    const studentId = getOrCreateStudentId();
    const userMessage = input.trim();
    setInput("");
    setLoading(true);

    const newMessages: ChatMessage[] = [
      ...messages,
      { role: "student", content: userMessage },
    ];
    setMessages(newMessages);

    try {
      const history: ConversationMessage[] = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await tutorApi.next(
        studentId,
        classCode,
        Number(assignmentId),
        Number(problemId),
        history,
        userMessage
      );

      setHintLevel(response.telemetry.hint_level_served);
      if (response.telemetry.policy_violation_prevented) {
        setViolationPrevented(true);
      }

      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: response.student_message,
          checkQuestion: response.check_question,
        },
      ]);
    } catch {
      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  }, [input, loading, messages, classCode, assignmentId, problemId]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-indigo-100 px-4 py-3 flex items-center gap-4 shadow-sm">
        <Link
          href={`/student/class/${classCode}/assignment/${assignmentId}`}
          className="text-indigo-600 hover:underline text-sm"
        >
          ← Back
        </Link>
        <div className="flex-1 min-w-0">
          <h1 className="font-semibold text-indigo-900 truncate">
            {problem ? problem.problem_text : "Loading problem..."}
          </h1>
          {problem?.skill_tags && problem.skill_tags.length > 0 && (
            <div className="flex gap-1 mt-0.5">
              {problem.skill_tags.map((t) => (
                <Badge key={t} variant="outline" className="text-xs">
                  {t}
                </Badge>
              ))}
            </div>
          )}
        </div>
        <Badge variant="secondary" className="shrink-0">
          Hint {hintLevel}
        </Badge>
        {violationPrevented && (
          <Badge variant="destructive" className="shrink-0 text-xs">
            Answer blocked
          </Badge>
        )}
      </header>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "student" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                msg.role === "student"
                  ? "bg-indigo-600 text-white rounded-br-sm"
                  : "bg-white text-gray-800 shadow-sm border border-indigo-100 rounded-bl-sm"
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              {msg.checkQuestion && msg.role === "assistant" && (
                <p className="text-xs mt-2 text-indigo-400 italic">{msg.checkQuestion}</p>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm border border-indigo-100">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-indigo-300 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-indigo-300 rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-indigo-300 rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="bg-white border-t border-indigo-100 p-3 shadow-md">
        <div className="max-w-3xl mx-auto flex gap-2 items-end">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your answer or question… (Enter to send, Shift+Enter for newline)"
            className="resize-none min-h-[52px] max-h-36 flex-1 focus:ring-2 focus:ring-indigo-400"
            rows={2}
            disabled={loading}
            autoFocus
          />
          <Button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            size="icon"
            className="h-12 w-12 shrink-0"
            aria-label="Send message"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-gray-400 text-center mt-1">
          This tutor won&apos;t give you the answer — it&apos;ll help you figure it out!
        </p>
      </div>
    </main>
  );
}
