import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Synapse — Interactive Science Learning",
  description:
    "A team of pedagogical agents diagnoses a student and composes the right interactive way to learn KSSM SPM science — Physics, Chemistry, Biology.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
