/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: { DEFAULT: "1.5rem", lg: "3rem" },
      screens: { "2xl": "1440px" },
    },
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      colors: {
        // Brand ZAGI
        zagi: {
          bg: "#08090c",            // deep void
          surface: "#0f1115",       // card
          surface2: "#15181f",      // raised
          border: "#1f232b",
          line: "#262b35",
          ink: "#e8eaf0",
          muted: "#7a8290",
          dim: "#4a5160",
          // Akcenty
          crimson: "#e50914",       // Netflix red
          crimson2: "#ff1f3d",
          neon: "#5eead4",          // cyan/teal glow
          neon2: "#22d3ee",
          violet: "#a78bfa",
          gold: "#fbbf24",
        },
        // Aliasy shadcn
        border: "#1f232b",
        input: "#15181f",
        ring: "#e50914",
        background: "#08090c",
        foreground: "#e8eaf0",
        primary: { DEFAULT: "#e50914", foreground: "#ffffff" },
        secondary: { DEFAULT: "#15181f", foreground: "#e8eaf0" },
        destructive: { DEFAULT: "#ef4444", foreground: "#ffffff" },
        muted: { DEFAULT: "#15181f", foreground: "#7a8290" },
        accent: { DEFAULT: "#15181f", foreground: "#5eead4" },
        popover: { DEFAULT: "#0f1115", foreground: "#e8eaf0" },
        card: { DEFAULT: "#0f1115", foreground: "#e8eaf0" },
      },
      borderRadius: {
        xl: "0.875rem",
        "2xl": "1.25rem",
        "3xl": "1.75rem",
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(229,9,20,0.55), 0 0 80px -20px rgba(229,9,20,0.25)",
        "glow-sm": "0 0 24px -6px rgba(229,9,20,0.45)",
        "glow-neon": "0 0 30px -6px rgba(94,234,212,0.5)",
        "card-up": "0 30px 60px -20px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.04)",
      },
      backgroundImage: {
        "grid-fade":
          "radial-gradient(circle at center, rgba(255,255,255,0.04) 1px, transparent 1px)",
        "mesh":
          "radial-gradient(at 20% 0%, rgba(229,9,20,0.18) 0px, transparent 50%), radial-gradient(at 80% 0%, rgba(94,234,212,0.15) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(167,139,250,0.12) 0px, transparent 50%)",
        "shine":
          "linear-gradient(110deg, transparent 25%, rgba(255,255,255,0.08) 50%, transparent 75%)",
      },
      keyframes: {
        "shimmer": { "0%": { backgroundPosition: "200% 0" }, "100%": { backgroundPosition: "-200% 0" } },
        "pulse-glow": {
          "0%,100%": { boxShadow: "0 0 0 0 rgba(229,9,20,0.45)" },
          "50%":     { boxShadow: "0 0 0 12px rgba(229,9,20,0)" },
        },
        "blob":      { "0%,100%": { transform: "translate(0,0) scale(1)" }, "33%": { transform: "translate(40px,-30px) scale(1.1)" }, "66%": { transform: "translate(-30px,40px) scale(0.95)" } },
        "float":     { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-8px)" } },
        "fade-up":   { "0%": { opacity: "0", transform: "translateY(12px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        "scan":      { "0%": { transform: "translateY(-100%)" }, "100%": { transform: "translateY(100%)" } },
      },
      animation: {
        "shimmer":    "shimmer 6s linear infinite",
        "pulse-glow": "pulse-glow 2s ease-out infinite",
        "blob":       "blob 14s ease-in-out infinite",
        "float":      "float 4s ease-in-out infinite",
        "fade-up":    "fade-up 0.6s ease-out both",
        "scan":       "scan 3s linear infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
