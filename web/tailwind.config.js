/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Segoe UI", "Helvetica Neue", "sans-serif"],
      },
      boxShadow: {
        card: "0 18px 40px rgba(2, 6, 23, 0.12)",
      },
    },
  },
  plugins: [],
};
