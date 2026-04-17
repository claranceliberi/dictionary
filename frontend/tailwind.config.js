/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        rw: {
          green: '#006B3E',
          'green-dark': '#00552F',
        },
        imigongo: {
          cream: '#F5F0E8',
          earth: '#8B3A2A',
          dark: '#1A1A1A',
        },
      },
      fontFamily: {
        serif: ['"Noto Serif"', 'Georgia', 'serif'],
        sans: ['"Noto Sans"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
