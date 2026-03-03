import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['var(--font-outfit)', 'sans-serif'],
        sans: ['var(--font-outfit)', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'monospace'],
      },
      backgroundImage: {
        "nexus-gradient": "linear-gradient(to bottom right, #020617, #0f172a, #172554)",
      },
      boxShadow: {
        // Claymorphism: deep outer shadow + subtle bright top inset + subtle dark bottom inset
        'clay-sm': '0 4px 10px rgba(0,0,0,0.3), inset 0 1px 1px rgba(255,255,255,0.15), inset 0 -1px 2px rgba(0,0,0,0.2)',
        'clay-md': '0 8px 20px rgba(0,0,0,0.4), inset 0 1px 2px rgba(255,255,255,0.15), inset 0 -2px 4px rgba(0,0,0,0.3)',
        'clay-lg': '0 12px 30px rgba(0,0,0,0.5), inset 0 2px 4px rgba(255,255,255,0.1), inset 0 -4px 8px rgba(0,0,0,0.4)',
        // Pressed state: inner shadows simulate depth inward
        'clay-pressed': 'inset 0 4px 8px rgba(0,0,0,0.6), inset 0 -1px 1px rgba(255,255,255,0.05)',
      },
      colors: {
        neon: {
          cyan: "#22d3ee",
          orange: "#fb923c",
          green: "#4ade80",
          pink: "#f472b6"
        },
        glass: {
          light: "rgba(255, 255, 255, 0.03)",
          medium: "rgba(255, 255, 255, 0.08)",
          heavy: "rgba(255, 255, 255, 0.15)",
          border: "rgba(255, 255, 255, 0.1)"
        }
      }
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
