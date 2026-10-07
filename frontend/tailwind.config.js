/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        cream: "#FFF9F1",
        ink: "#2B211B",
        cinnamon: "#D86A2E",
        caramel: "#B94D20",
        sand: "#F1E7DA",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["DM Sans", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 18px 50px rgba(66, 42, 24, 0.08)",
      },
    },
  },
  plugins: [],
};
