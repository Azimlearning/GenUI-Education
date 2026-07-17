import type { Metadata } from "next";
import { Fredoka, Nunito, JetBrains_Mono } from "next/font/google";
import "./globals.css";

// Self-hosted via next/font (no runtime CDN, no layout shift). See design/BRAND.md
// section 5. Fredoka = display, Nunito = body/UI, JetBrains Mono = the instrument
// texture (the doc names Berkeley Mono with JetBrains Mono as the shippable fallback).
const display = Fredoka({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-display",
  display: "swap",
});
const sans = Nunito({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});
const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Axiom",
  description: "Ask a science question. Watch it get built, and checked.",
};

// Set the theme before first paint so there is no light-to-dark flash. Reads a
// saved choice, else the system preference. The top-bar toggle updates both.
const themeScript = `try{var t=localStorage.getItem('axiom-theme');if(t!=='light'&&t!=='dark'){t=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}document.documentElement.dataset.theme=t;}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${display.variable} ${sans.variable} ${mono.variable}`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="min-h-screen font-sans antialiased">{children}</body>
    </html>
  );
}
