/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#141414",
        secondary: "#1A1A1A",
        accent: "#4F46E5",
        textMain: "#F3F4F6",
        textMuted: "#9CA3AF"
      }
    },
  },
  plugins: [],
}
