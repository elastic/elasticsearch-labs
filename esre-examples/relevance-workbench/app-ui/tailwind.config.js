/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'elastic-blue-dark': '#041B39',
        'elastic-blue': '#1D4290',
        'elastic-blue-light': '#2058CB',
        'elastic-blue-lighter': '#008EF0',
      },
      fontFamily: {
        sans: ['Space Grotesk', ...defaultTheme.fontFamily.sans],
        mono: ['Space Mono', ...defaultTheme.fontFamily.mono],
      }
    },
  },
  plugins: [
    require('@tailwindcss/line-clamp'),
  ],
}
