/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        'poppins': ['Poppins', 'sans-serif'],
        'franklin': ['"Franklin Gothic Medium"', '"Arial Narrow"', 'Arial', 'sans-serif'],
        'roboto': ['Roboto', 'sans-serif'],
        'arial': ['Arial', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
