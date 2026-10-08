/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        angel: {
          orange: '#FF5722',
          blue: '#0F172A',
          card: '#1E293B',
          border: '#334155'
        }
      }
    },
  },
  plugins: [],
}
