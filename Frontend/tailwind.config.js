/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/components/**/*.{js,vue,ts}",
    "./app/layouts/**/*.vue",
    "./app/pages/**/*.vue",
    "./app/plugins/**/*.{js,ts}",
    "./app/app.vue",
    "./app/error.vue",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          green: '#1A3C3B',  // Original Deep Teal
          dark: '#1A3C3B',   // Mapped to Green for safety as original didn't have separate 'dark'
          gold: '#A08050',   // Original Bronze/Gold
          cream: '#E4E4E4',  // Original Light Gray
        }
      },
      fontFamily: {
        // Keep the fonts as they were likely fine/not the main issue, but reverting to original sans stack if needed.
        // I'll keep the new fonts (Cinzel/Lato) as "better fonts" was requested earlier and might still be desired, 
        // but the COLOR palette was the main complaint. 
        // Actually I'll keep them but map them safely.
        serif: ['Cinzel', 'serif'],
        sans: ['Lato', 'sans-serif'],
        script: ['Great Vibes', 'cursive'],
        display: ['"Fleur De Leah"', 'cursive'],
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
