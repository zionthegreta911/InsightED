/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./resources/**/*.blade.php",
      "./resources/**/*.js",
      "./resources/**/*.jsx",
    ],
    theme: {
      extend: {
        fontFamily: {
          sans: ["Poppins", "sans-serif"],  // Apply Poppins globally
        },
      },
    },
    plugins: [],
  };
  