import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MindOS AI — Your Mental Wellness Companion",
  description:
    "An empathetic AI companion that listens, understands, and supports your mental wellbeing through voice and text conversations with long-term memory.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#0a0a1a" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧠</text></svg>" />
      </head>
      <body>{children}</body>
    </html>
  );
}
