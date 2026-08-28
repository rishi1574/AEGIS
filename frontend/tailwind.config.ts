import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Elite Enterprise Light Theme Palette
        vanguard: {
          bg: "#fafafb", // Ultra light gray/blue tint
          surface: "#ffffff",
          card: "#ffffff",
          border: "#eaebf0",
          "border-active": "#f15a22", // Mastercard primary orange
          text: "#1e293b",
          "text-muted": "#64748b",
          
          // Red Team (Threat) Colors
          red: {
            DEFAULT: "#d92d20", // Deep sophisticated red
            light: "#fee4e2",
            glow: "#d92d2020",
          },
          
          // Blue Team (Defense) Colors
          blue: {
            DEFAULT: "#1a1f71", // Authentic Mastercard Navy
            light: "#e0e7ff",
            glow: "#1a1f7120",
          },
          
          // Success/Metrics Colors
          green: {
            DEFAULT: "#027a48", // Enterprise green
            light: "#d1fadf",
            glow: "#027a4820",
          },
          
          // Warnings/Anomalies
          amber: {
            DEFAULT: "#b54708", // Deep amber
            light: "#fef0c7",
          },
          
          // Accent
          purple: {
            DEFAULT: "#6941c6",
            light: "#f4f3ff",
          },
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
