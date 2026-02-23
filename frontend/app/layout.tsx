import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Figure It Out",
  description: "Integrity-first AI tutor + teacher analytics",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui, -apple-system, sans-serif" }}>{children}</body>
    </html>
  );
}
