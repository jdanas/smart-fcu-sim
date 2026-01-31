import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Primary monotone palette (Slate-based)
        background: "#0a0a0b",
        foreground: "#fafafa",

        // Card surfaces
        card: {
          DEFAULT: "#141416",
          foreground: "#e4e4e7",
        },

        // Muted elements
        muted: {
          DEFAULT: "#27272a",
          foreground: "#a1a1aa",
        },

        // Borders and separators
        border: "#3f3f46",
        input: "#27272a",
        ring: "#52525b",

        // Primary accent (subtle slate)
        primary: {
          DEFAULT: "#71717a",
          foreground: "#fafafa",
        },

        // Secondary
        secondary: {
          DEFAULT: "#18181b",
          foreground: "#d4d4d8",
        },

        // Semantic colors (minimal use)
        destructive: {
          DEFAULT: "#dc2626",
          foreground: "#fafafa",
        },
        success: {
          DEFAULT: "#16a34a",
          foreground: "#fafafa",
        },

        // Chart-specific
        chart: {
          current: "#d4d4d8",
          predicted: "#71717a",
          grid: "#27272a",
          area: "rgba(113, 113, 122, 0.1)",
        },

        // Accent for highlights
        accent: {
          DEFAULT: "#3f3f46",
          foreground: "#fafafa",
        },
      },

      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },

      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
