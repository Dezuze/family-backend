declare const process: any;

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  // point to the Tailwind entry in the Nuxt app folder
  css: ['/assets/css/tailwind.css'],
  postcss: {
    plugins: {
      "@tailwindcss/postcss": {},
    },
  },
  googleFonts: {
    fontsDir: './assets/fonts',
    families: {
      Arima: [400, 700],
      Itim: [400, 700],
      'Noto Sans Malayalam': [400, 500, 700],
      'Noto Serif Malayalam': [400, 700],
    },
    display: 'swap',
    prefetch: true,
    download: true,
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE || 'http://localhost:8000',
      // Respect env var; default to false (call backend by default)
      localAuth: process.env.LOCAL_AUTH === 'true' ? true : false,
      // Public site URL used for canonical links, sitemap and robots
      siteUrl: process.env.SITE_URL || 'http://localhost:3000',
    },
  },

  modules: [
    'nuxt-aos',
    '@formkit/auto-animate',
    '@nuxtjs/color-mode',
    '@nuxtjs/google-fonts',
    '@nuxtjs/i18n',
    '@pinia/nuxt',
    '@pinia-plugin-persistedstate/nuxt',
  ],

  i18n: {
    defaultLocale: 'en',
    strategy: 'no_prefix',
    lazy: true,
    langDir: 'locales',
    detectBrowserLanguage: false,
    locales: [
      { code: 'en', name: 'English', file: 'en.json' },
      { code: 'ml', name: 'Malayalam', file: 'ml.json' },
    ],
  },
})
