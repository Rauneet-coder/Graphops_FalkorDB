import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GraphOps — SRE Incident Investigation",
  description: "AI-powered SRE incident investigation system using FalkorDB",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
