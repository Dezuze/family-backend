import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  content: [
    './app/**/*.{vue,ts,js,html}',
    './components/**/*.{vue,ts,js,html}',
    './pages/**/*.{vue,ts,js,html}',
  ],
  theme: {
    extend: {
       fontFamily: {
        arima: ['Arima', 'cursive'],
        itim: ['Itim', 'cursive'],
      },
      colors: {
        brand: {
          gold: '#CDAA7D',
          olive: '#556B2F',
          slate: '#2F4F4F',
          dark: '#0D0D0D',
          light: '#F9F9F7',
          white: '#FFFFFF',
        },
      },
    },
  },
}
