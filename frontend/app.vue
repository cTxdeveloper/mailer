<template>
  <v-app :theme="isDark ? 'darkTheme' : 'lightTheme'">
    <NuxtLayout>
      <NuxtLoadingIndicator color="#7F5AF0" :height="3" />
      <Toaster position="top-right" richColors closeButton />
      <NuxtPage />
    </NuxtLayout>
  </v-app>
</template>

<script setup lang="ts">
import { Toaster } from 'vue-sonner';
import { useUiStore } from '~/store/ui'; // Assuming you have a UI store for theme
import { computed } from 'vue';

const uiStore = useUiStore();
const isDark = computed(() => uiStore.isDarkMode); // Example, adapt to your store

// Define Vuetify themes
const lightTheme = {
  dark: false,
  colors: {
    background: '#F4F5F7', // Light grey background
    surface: '#FFFFFF', // White surface for cards, etc.
    primary: '#7F5AF0', // Quantum Purple
    'primary-darken-1': '#6A48D0',
    secondary: '#2CB67D', // Guardian Green
    'secondary-darken-1': '#1F9A65',
    error: '#EF4444',
    info: '#2196F3',
    success: '#2CB67D',
    warning: '#F59E0B',
    'on-background': '#101014', // Obsidian Black for text on light background
    'on-surface': '#101014',
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    'on-error': '#FFFFFF',
    'on-info': '#FFFFFF',
    'on-success': '#FFFFFF',
    'on-warning': '#FFFFFF',
  }
};

const darkTheme = {
  dark: true,
  colors: {
    background: '#101014', // Obsidian Black
    surface: '#1E1E22', // Slightly lighter black for surfaces
    primary: '#7F5AF0', // Quantum Purple
    'primary-darken-1': '#6A48D0',
    secondary: '#2CB67D', // Guardian Green
    'secondary-darken-1': '#1F9A65',
    error: '#CF6679', // Material dark error
    info: '#2196F3', // Standard info
    success: '#2CB67D',
    warning: '#FB8C00', // Material dark warning
    'on-background': '#E0E0E0', // Light grey text on dark background
    'on-surface': '#FFFFFF', // Pure white for text on dark surfaces
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    'on-error': '#000000',
    'on-info': '#000000',
    'on-success': '#000000',
    'on-warning': '#000000',
  }
};

// Provide themes to Vuetify instance (alternative to doing it in vuetify plugin directly)
// This might be overridden or complemented by how Vuetify is setup in plugins/vuetify.ts
// For Nuxt 3, Vuetify setup is typically in a plugin.

useHead({
  titleTemplate: (titleChunk) => {
    return titleChunk ? `${titleChunk} - Access Marketplace` : 'Access Marketplace';
  },
  htmlAttrs: {
    lang: 'en'
  },
  bodyAttrs: {
    class: 'bg-obsidian-black text-pure-white antialiased font-sans' // Base styling
  }
});

// Initialize Lenis for smooth scrolling if not done elsewhere
onMounted(async () => {
  if (process.client) {
    const Lenis = (await import('lenis')).default;
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // https://www.desmos.com/calculator/brs54l4xou
    });

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // Optional: Sync with GSAP ticker for better animation performance
    // gsap.ticker.add((time)=>{
    //   lenis.raf(time * 1000);
    // });
    // gsap.ticker.lagSmoothing(0);
  }
});
</script>

<style lang="scss">
// Global styles, can also be in main.css

// Import fonts (example, ensure you have them locally or via CDN)
// @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Satoshi:wght@400;500;700;900&display=swap');

body {
  background-color: var(--v-theme-background);
  color: var(--v-theme-on-background);
}

// Basic scrollbar styling for a more modern look
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #1e1e22; // Dark track
}
::-webkit-scrollbar-thumb {
  background: #7F5AF0; // Purple thumb
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #6A48D0; // Darker purple on hover
}

// Page transitions (example)
.page-enter-active,
.page-leave-active {
  transition: all 0.4s ease-in-out;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.layout-enter-active,
.layout-leave-active {
  transition: all 0.4s ease-in-out;
}
.layout-enter-from,
.layout-leave-to {
  opacity: 0;
  filter: blur(1rem);
}
</style>
