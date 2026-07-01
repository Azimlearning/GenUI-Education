import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";
import "./globals.css";

// Editorial pairing: a characterful serif for display headings (credible, academic),
// a clean neutral sans for body/UI. Exposed as CSS variables consumed in globals.css.
const fraunces = Fraunces({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-display",
  display: "swap",
});
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Synapse — Interactive Science Learning",
  description:
    "A team of pedagogical agents diagnoses a student and composes the right interactive way to learn KSSM SPM science — Physics, Chemistry, Biology.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${fraunces.variable} ${inter.variable}`}>
      <body>{children}</body>
    </html>
  );
}
