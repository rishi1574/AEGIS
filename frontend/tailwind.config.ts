import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Minimalist Mastercard-inspired light theme
        aegis: {
          bg: "#f8fafc",
          surface: "#ffffff",
          card: "#ffffff",
          border: "#e2e8f0",
          "border-active": "#f97316", // Orange accent
          text: "#0f172a",
          "text-muted": "#64748b",
          // Red Team colors (Orange/Red)
          red: "#eb3c00",
          "red-glow": "#eb3c0020",
          "red-bg": "#eb3c0010",
          // Blue Team colors (Mastercard Blue)
          blue: "#1a1f71",
          "blue-glow": "#1a1f7120",
          "blue-bg": "#1a1f7110",
          // Accent
          green: "#10b981",
          amber: "#f59e0b",
          purple: "#8b5cf6",
          cyan: "#06b6d4",
        },
      },
      fontFamily: {
        sans: ["Outfit", "system-ui", "sans-serif"],
        mono: ["Inter", "monospace"],
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
          "0%, 100%": { boxShadow: "0 0 5px #eb3c00, 0 0 10px #eb3c0020" },
          "50%": { boxShadow: "0 0 15px #eb3c00, 0 0 20px #eb3c0040" },
        },
        "glow-blue": {
          "0%, 100%": { boxShadow: "0 0 5px #1a1f71, 0 0 10px #1a1f7120" },
          "50%": { boxShadow: "0 0 15px #1a1f71, 0 0 20px #1a1f7140" },
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
        "grid-pattern": "none",
      },
    },
  },
  plugins: [],
};
export default config;
