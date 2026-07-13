import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GenUI test v2 — Level 2 Generative UI",
  description:
    "Proof of concept: the model returns a declarative UI spec, the client renders it.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
