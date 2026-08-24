/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        lenny: {
          dark: '#0f172a',
          card: '#1e293b',
          accent: '#6366f1',
          orange: '#f97316',
          emerald: '#10b981',
          border: '#334155'
        }
      }
    },
  },
  plugins: [],
}
