/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        vesper: {
          bg:       "#080c14",
          surface:  "#0d1526",
          card:     "#111d33",
          border:   "#1a2d4a",
          cyan:     "#00d4ff",
          blue:     "#0057ff",
          green:    "#00ff88",
          amber:    "#ffaa00",
          red:      "#ff3b5c",
          muted:    "#4a6080",
          text:     "#c8d8f0",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow:       "0 0 20px rgba(0, 212, 255, 0.15)",
        "glow-green": "0 0 20px rgba(0, 255, 136, 0.15)",
        "glow-red":   "0 0 20px rgba(255, 59, 92, 0.15)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "fade-in":    "fadeIn 0.4s ease-out",
        "slide-up":   "slideUp 0.3s ease-out",
      },
      keyframes: {
        fadeIn:  { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp: { "0%": { transform: "translateY(8px)", opacity: "0" }, "100%": { transform: "translateY(0)", opacity: "1" } },
      },
    },
  },
  plugins: [],
};
