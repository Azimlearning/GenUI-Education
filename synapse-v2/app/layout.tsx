import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Synapse — your question, as a lab",
  description:
    "Generative-UI science labs for Malaysian Form 4-5 KSSM SPM students. Ask a question, get an interactive experiment you can run.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
