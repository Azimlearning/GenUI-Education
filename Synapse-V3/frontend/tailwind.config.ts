import type { Config } from "tailwindcss";

/**
 * Theme tokens implement design/BRAND.md. Components read semantic names
 * (bg-card, text-ink-dim, text-primary), never raw hex. The values live as
 * CSS variables in app/globals.css so there is a single source of truth.
 */
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "var(--canvas)",
        band: "var(--band)",
        card: "var(--card)",
        ink: {
          DEFAULT: "var(--ink)",
          dim: "var(--ink-dim)",
          faint: "var(--ink-faint)",
        },
        line: {
          DEFAULT: "var(--line)",
          2: "var(--line-2)",
        },
        primary: {
          DEFAULT: "var(--primary)",
          btn: "var(--primary-btn)",
          edge: "var(--primary-edge)",
          soft: "var(--primary-soft)",
          ink: "var(--primary-ink)",
          line: "var(--primary-line)",
        },
        verify: {
          DEFAULT: "var(--verify)",
          edge: "var(--verify-edge)",
          soft: "var(--verify-soft)",
          ink: "var(--verify-ink)",
        },
        gold: {
          DEFAULT: "var(--gold)",
          soft: "var(--gold-soft)",
        },
        warn: "var(--warn)",
        danger: "var(--danger)",
      },
      fontFamily: {
        display: ["var(--font-display)", "Trebuchet MS", "system-ui", "sans-serif"],
        sans: [
          "var(--font-sans)",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      borderRadius: {
        ctl: "12px",
        card: "18px",
        frame: "24px",
      },
      boxShadow: {
        card: "0 8px 26px -10px rgb(20 55 45 / 0.16)",
        frame:
          "0 22px 54px -20px rgb(11 60 50 / 0.26), 0 4px 12px -4px rgb(15 40 35 / 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
