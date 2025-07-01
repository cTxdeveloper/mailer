// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: true, // Enable SSR for SEO and performance

  app: {
    head: {
      title: 'The Access Marketplace',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { hid: 'description', name: 'description', content: 'Unlock your network. Connect with value.' },
        { name: 'msapplication-TileColor', content: '#7f5af0' },
        { name: 'theme-color', content: '#101014' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32x32.png' },
        { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-16x16.png' },
        { rel: 'manifest', href: '/site.webmanifest' }
      ],
    }
  },

  css: [
    '~/assets/css/main.css',
    'vuetify/lib/styles/main.sass',
    '@mdi/font/css/materialdesignicons.min.css',
  ],

  modules: [
    '@pinia/nuxt',
    '@vee-validate/nuxt',
    '@vueuse/nuxt',
    'nuxt-phosphor-icons',
    // Vuetify module configuration is handled by vite-plugin-vuetify
  ],

  build: {
    transpile: ['vuetify', 'gsap'], // Transpile Vuetify and GSAP for compatibility
  },

  vite: {
    define: {
      'process.env.DEBUG': false,
    },
    // Vuetify plugin for tree-shaking and auto-imports
    plugins: [
      // Vuetify(), // This will be handled by another way if not using the nuxt module for vuetify
    ],
  },

  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },

  pinia: {
    autoImports: [
      'defineStore',
      ['defineStore', 'definePiniaStore'],
    ],
  },

  veeValidate: {
    // Global configuration
    autoImports: true,
    // Component names
    componentNames: {
      Form: 'VeeForm',
      Field: 'VeeField',
      FieldArray: 'VeeFieldArray',
      ErrorMessage: 'VeeErrorMessage',
    },
  },

  phosphor: {
    prefix: 'Ph', // Optional: You can set a prefix for icon components
    showCollections: true // Optional: Displays collection names in verbose mode
  },

  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
      gtagId: process.env.NUXT_PUBLIC_GTAG_ID || '', // For Google Analytics
    }
  },
});
