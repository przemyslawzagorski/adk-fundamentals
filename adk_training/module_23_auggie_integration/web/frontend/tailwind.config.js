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
        // Brand: Concierge — deep navy + electric blue
        cnc: {
          bg: "#020617",          // void deep navy
          surface: "#0b1224",     // card
          surface2: "#111a31",    // raised
          border: "#1e293b",
          line: "#243049",
          ink: "#e2e8f0",
          muted: "#7d8aa3",
          dim: "#475569",
          // Akcenty: blue/cyan/azure
          azure: "#1e40af",       // deep granat
          azure2: "#1d4ed8",
          electric: "#3b82f6",    // electric blue (primary)
          electric2: "#60a5fa",   // softer
          cyan: "#22d3ee",        // accent neon
          cyan2: "#67e8f9",
          gold: "#fbbf24",        // warning/highlight
          rose: "#fb7185",        // error
        },
        // Aliasy shadcn
        border: "#1e293b",
        input: "#0b1224",
        ring: "#3b82f6",
        background: "#020617",
        foreground: "#e2e8f0",
        primary: { DEFAULT: "#3b82f6", foreground: "#ffffff" },
        secondary: { DEFAULT: "#0b1224", foreground: "#e2e8f0" },
        destructive: { DEFAULT: "#fb7185", foreground: "#ffffff" },
        muted: { DEFAULT: "#0b1224", foreground: "#7d8aa3" },
        accent: { DEFAULT: "#0b1224", foreground: "#22d3ee" },
        popover: { DEFAULT: "#0b1224", foreground: "#e2e8f0" },
        card: { DEFAULT: "#0b1224", foreground: "#e2e8f0" },
      },
      borderRadius: {
        xl: "0.875rem",
        "2xl": "1.25rem",
        "3xl": "1.75rem",
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(59,130,246,0.55), 0 0 80px -20px rgba(34,211,238,0.25)",
        "glow-sm": "0 0 24px -6px rgba(59,130,246,0.5)",
        "glow-cyan": "0 0 30px -6px rgba(34,211,238,0.55)",
        "glow-azure": "0 0 50px -10px rgba(30,64,175,0.7)",
        "card-up": "0 30px 60px -20px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.04)",
      },
      backgroundImage: {
        "mesh":
          "radial-gradient(at 18% 0%, rgba(30,64,175,0.35) 0px, transparent 55%), radial-gradient(at 82% 0%, rgba(34,211,238,0.20) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(59,130,246,0.18) 0px, transparent 55%)",
        "shine":
          "linear-gradient(110deg, transparent 25%, rgba(255,255,255,0.08) 50%, transparent 75%)",
        "azure-grad": "linear-gradient(135deg,#1e40af 0%,#3b82f6 50%,#22d3ee 100%)",
      },
      keyframes: {
        "shimmer": { "0%": { backgroundPosition: "200% 0" }, "100%": { backgroundPosition: "-200% 0" } },
        "pulse-glow": {
          "0%,100%": { boxShadow: "0 0 0 0 rgba(59,130,246,0.5)" },
          "50%":     { boxShadow: "0 0 0 12px rgba(59,130,246,0)" },
        },
        "blob": {
          "0%,100%": { transform: "translate(0,0) scale(1)" },
          "33%": { transform: "translate(40px,-30px) scale(1.1)" },
          "66%": { transform: "translate(-30px,40px) scale(0.95)" },
        },
        "float": { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-8px)" } },
        "fade-up": { "0%": { opacity: "0", transform: "translateY(12px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        "scan": { "0%": { transform: "translateY(-100%)" }, "100%": { transform: "translateY(100%)" } },
        "gradient-x": { "0%,100%": { backgroundPosition: "0% 50%" }, "50%": { backgroundPosition: "100% 50%" } },
      },
      animation: {
        "shimmer": "shimmer 6s linear infinite",
        "pulse-glow": "pulse-glow 2s ease-out infinite",
        "blob": "blob 14s ease-in-out infinite",
        "float": "float 4s ease-in-out infinite",
        "fade-up": "fade-up 0.6s ease-out both",
        "scan": "scan 3s linear infinite",
        "gradient-x": "gradient-x 8s ease infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
