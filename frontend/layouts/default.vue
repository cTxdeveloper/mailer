<template>
  <v-app class="app-container" :class="{ 'dark-theme': uiStore.isDarkMode, 'light-theme': !uiStore.isDarkMode }">
    <LayoutAppHeader />
    <v-main class="main-content pt-16 bg-obsidian-black">
      <v-container fluid class="pa-0 fill-height">
        <div class="content-wrapper w-full noise-bg">
          <Transition name="page" mode="out-in">
            <slot />
          </Transition>
        </div>
      </v-container>
    </v-main>
    <LayoutAppFooter />
    <!-- Global components like a full-screen loader can be placed here -->
    <UiAppLoader :fullscreen="true" v-if="uiStore.isGlobalLoading" message="Processing..." />
  </v-app>
</template>

<script setup lang="ts">
import LayoutAppHeader from '~/components/layout/AppHeader.vue';
import LayoutAppFooter from '~/components/layout/AppFooter.vue';
import UiAppLoader from '~/components/ui/AppLoader.vue'; // Assuming this is your global loader
import { useUiStore } from '~/store/ui';

const uiStore = useUiStore();

useHead({
  bodyAttrs: {
    class: 'default-layout-body' // Specific class for default layout body if needed
  }
});

// You can add watchers or other layout-specific logic here
// For example, listening to route changes to perform actions

// Example of using runtimeConfig if needed in layout
// const config = useRuntimeConfig();
// console.log('API Base URL from layout:', config.public.apiBaseUrl);
</script>

<style scoped lang="scss">
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: background-color 0.3s ease; /* Smooth theme transition */
}

.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  // The pt-16 is to offset for the fixed AppHeader, adjust if header height changes
  // background-color: var(--v-theme-background); // Vuetify handles this based on theme
}

.content-wrapper {
  padding: 1rem; /* Default padding, can be overridden by page */
  @media (min-width: 768px) {
    padding: 1.5rem; /* Larger padding for md screens and up */
  }
  @media (min-width: 1024px) {
    padding: 2rem; /* Even larger for lg screens */
  }
  // The noise-bg class from main.css adds a subtle noise texture
}

/* Page transitions (can be customized further) */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(15px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}

// Ensure Vuetify theming applies correctly
.light-theme {
  // background-color: #F4F5F7; /* Light grey background from theme */
  // color: #101014; /* Obsidian Black text */
}
.dark-theme {
  // background-color: #101014; /* Obsidian Black background */
  // color: #E0E0E0; /* Light grey text */
}

// Ensure footer doesn't overlap content if content is short
// This is generally handled by v-main flex-grow: 1 and v-app display:flex, flex-direction:column
</style>
