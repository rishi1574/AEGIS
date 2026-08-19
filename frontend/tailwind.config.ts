import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Cybersecurity dark theme palette
        aegis: {
          bg: "#0a0e17",
          surface: "#111827",
          card: "#1a2235",
          border: "#1e293b",
          "border-active": "#3b82f6",
          text: "#e2e8f0",
          "text-muted": "#94a3b8",
          // Red Team colors
          red: "#ef4444",
          "red-glow": "#dc262640",
          "red-bg": "#7f1d1d20",
          // Blue Team colors
          blue: "#3b82f6",
          "blue-glow": "#3b82f640",
          "blue-bg": "#1e3a5f20",
          // Accent
          green: "#22c55e",
          amber: "#f59e0b",
          purple: "#a855f7",
          cyan: "#06b6d4",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "pulse-slow": "pulse 3s ease-in-out infinite",
        "glow-red": "glow-red 2s ease-in-out infinite",
        "glow-blue": "glow-blue 2s ease-in-out infinite",
        "scan-line": "scan-line 4s linear infinite",
        "fade-in": "fade-in 0.5s ease-out",
        "slide-up": "slide-up 0.5s ease-out",
      },
      keyframes: {
        "glow-red": {
          "0%, 100%": { boxShadow: "0 0 5px #ef4444, 0 0 10px #ef444440" },
          "50%": { boxShadow: "0 0 15px #ef4444, 0 0 30px #ef444460" },
        },
        "glow-blue": {
          "0%, 100%": { boxShadow: "0 0 5px #3b82f6, 0 0 10px #3b82f640" },
          "50%": { boxShadow: "0 0 15px #3b82f6, 0 0 30px #3b82f660" },
        },
        "scan-line": {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100vh)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      backgroundImage: {
        "grid-pattern": "linear-gradient(#1e293b 1px, transparent 1px), linear-gradient(90deg, #1e293b 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};
export default config;
