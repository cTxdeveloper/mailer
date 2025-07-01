<template>
  <v-app class="landing-app-container" :class="{ 'dark-theme': uiStore.isDarkMode, 'light-theme': !uiStore.isDarkMode }">
    <!-- Optional: A simplified header for the landing page or no header -->
    <LayoutAppHeader />
    <!-- <LayoutLandingHeader v-if="showHeader" /> -->

    <v-main class="landing-main-content">
      <!-- NuxtPage is where the content of pages/index.vue (or other landing pages) will be rendered -->
      <Transition name="page-fade" mode="out-in">
        <slot />
      </Transition>
    </v-main>

    <!-- Optional: A specific footer for the landing page or a simplified one -->
    <LayoutAppFooter />
    <!-- <LayoutLandingFooter v-if="showFooter" /> -->

    <!-- Global components like a full-screen loader can be placed here if needed -->
    <UiAppLoader :fullscreen="true" v-if="uiStore.isGlobalLoading" message="Loading Experience..." />
  </v-app>
</template>

<script setup lang="ts">
// Import specific landing page header/footer if they exist
// import LayoutLandingHeader from '~/components/layout/LandingHeader.vue';
// import LayoutLandingFooter from '~/components/layout/LandingFooter.vue';
import LayoutAppHeader from '~/components/layout/AppHeader.vue'; // Using the default header for now
import LayoutAppFooter from '~/components/layout/AppFooter.vue'; // Using the default footer for now
import UiAppLoader from '~/components/ui/AppLoader.vue';
import { useUiStore } from '~/store/ui';

const uiStore = useUiStore();

// Props to control visibility of header/footer, can be set by page meta
// const showHeader = computed(() => useRoute().meta.showHeader !== false);
// const showFooter = computed(() => useRoute().meta.showFooter !== false);

useHead({
  bodyAttrs: {
    class: 'landing-layout-body bg-obsidian-black' // Specific class for landing layout body
                                     // Ensures dark background even if theme switches
  }
});

// Landing page specific logic, e.g., animations, scroll behaviors
onMounted(() => {
  // Example: Initialize scroll animations or specific behaviors for landing page
  // if (process.client) {
  //   // const AOS = await import('aos');
  //   // AOS.init({ once: true, duration: 800, easing: 'ease-out-quad' });
  // }
});
</script>

<style scoped lang="scss">
.landing-app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #101014; // Enforce Obsidian Black for landing page consistency
  transition: background-color 0.3s ease; // Smooth theme transition (though likely always dark)
}

.landing-main-content {
  flex-grow: 1;
  display: flex; /* Allows content to fill height if needed */
  flex-direction: column; /* Stack content vertically */
  // No padding by default, pages should manage their own main content padding
  // background-color: var(--v-theme-background); // Vuetify handles this for v-main
}

/* Page transitions for landing page (can be different from default layout) */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.5s ease-in-out;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

// Override default layout theme classes if needed for landing page
// to ensure it always has the dark, cinematic feel.
.landing-layout-body {
  // background-color: #101014 !important; // Force obsidian black
  // color: #FFFFFF !important; // Force pure white text
}

// Ensure Vuetify theming applies correctly if not overridden
.light-theme.landing-app-container {
  // background-color: #101014; // Still prefer dark for landing
}
.dark-theme.landing-app-container {
  // background-color: #101014;
}

// If using a specific LandingHeader/Footer, style them here or in their components.
</style>
