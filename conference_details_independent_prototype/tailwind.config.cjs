/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f3f6ff",
          100: "#e6ecff",
          200: "#c9d7ff",
          300: "#a0b7ff",
          400: "#748fff",
          500: "#4b6cff",
          600: "#2f53ff",
          700: "#2541d9",
          800: "#1f37b0",
          900: "#1c318a",
        },
        ink: {
          50: "#f7f8fb",
          100: "#eef1f7",
          200: "#d9e0ee",
          300: "#b6c2d9",
          400: "#8f9bb3",
          500: "#6b768f",
          600: "#515a73",
          700: "#3a4156",
          800: "#2a2f3f",
          900: "#1d202b",
        },
      },
      boxShadow: {
        soft: "0 20px 40px -30px rgba(31, 55, 176, 0.4)",
        card: "0 12px 30px -20px rgba(31, 55, 176, 0.35)",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem",
      },
    },
  },
  plugins: [],
};
