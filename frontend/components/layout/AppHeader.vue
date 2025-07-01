<template>
  <v-app-bar
    app
    color="obsidian-black"
    dark
    elevate-on-scroll
    elevation="4"
    class="app-header glass-effect !border-b-0"
    style="backdrop-filter: blur(12px); background-color: rgba(18,18,22,0.7);"
  >
    <v-container class="pa-0 fill-height flex items-center">
      <NuxtLink to="/" class="flex items-center mr-6 text-decoration-none">
        <!-- <NexusLogo class="h-8 w-auto text-quantum-purple" /> -->
        <img src="/nexus-logo-light.svg" alt="Access Marketplace Logo" class="h-8 w-auto mr-2">
        <v-toolbar-title class="font-display text-pure-white text-xl font-bold">
          Access Marketplace
        </v-toolbar-title>
      </NuxtLink>

      <v-spacer></v-spacer>

      <!-- Desktop Navigation -->
      <nav class="hidden md:flex items-center space-x-2">
        <NuxtLink
          v-for="item in navigation"
          :key="item.name"
          :to="item.href"
          custom
          v-slot="{ navigate, isActive }"
        >
          <v-btn
            :active="isActive"
            text
            @click="navigate"
            class="font-semibold"
            :class="isActive ? 'text-quantum-purple' : 'text-gray-300 hover:text-pure-white'"
          >
            {{ item.name }}
          </v-btn>
        </NuxtLink>
      </nav>

      <v-spacer></v-spacer>

      <div class="flex items-center space-x-3">
        <AppButton
          v-if="!authStore.isAuthenticated"
          to="/auth/login"
          color="quantum-purple"
          size="small"
          class="font-semibold"
        >
          Login
        </AppButton>
        <AppButton
          v-if="!authStore.isAuthenticated"
          to="/auth/register"
          variant="outline"
          color="pure-white"
          size="small"
          class="font-semibold !border-pure-white/50 hover:!border-pure-white"
        >
          Sign Up
        </AppButton>

        <LayoutUserNav v-if="authStore.isAuthenticated" />

        <v-btn icon @click="toggleTheme" class="text-gray-300 hover:text-pure-white">
          <PhMoon v-if="!uiStore.isDarkMode" weight="fill" class="text-xl" />
          <PhSun v-else weight="fill" class="text-xl" />
        </v-btn>
      </div>

      <!-- Mobile Menu Button -->
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" class="md:hidden text-gray-300 hover:text-pure-white"></v-app-bar-nav-icon>
    </v-container>
  </v-app-bar>

  <!-- Mobile Navigation Drawer -->
  <v-navigation-drawer
    v-model="drawer"
    app
    temporary
    right
    color="obsidian-black"
    class="md:hidden glass-effect"
    style="backdrop-filter: blur(12px); background-color: rgba(18,18,22,0.9);"
  >
    <v-list nav dense>
      <v-list-item
        v-for="item in navigation"
        :key="item.name"
        :to="item.href"
        link
        class="hover:bg-quantum-purple/10"
      >
        <template v-slot:prepend>
          <component :is="item.icon" class="mr-3 text-quantum-purple" size="20" />
        </template>
        <v-list-item-title class="font-semibold text-pure-white">{{ item.name }}</v-list-item-title>
      </v-list-item>
    </v-list>
    <template v-slot:append>
      <div class="pa-2">
        <AppButton v-if="!authStore.isAuthenticated" to="/auth/login" block class="mb-2">Login</AppButton>
        <AppButton v-if="!authStore.isAuthenticated" to="/auth/register" variant="outline" block>Sign Up</AppButton>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '~/store/auth';
import { useUiStore } from '~/store/ui';
// import NexusLogo from '~/assets/svg/nexus-logo.svg'; // Ensure this path is correct or use an <img> tag

// Import Phosphor icons (ensure nuxt-phosphor-icons is set up)
import { PhHouse, PhMagnifyingGlass, PhPaperPlaneTilt, PhScroll, PhUserCircle } from 'phosphor-vue';

const authStore = useAuthStore();
const uiStore = useUiStore();

const drawer = ref(false);

const navigation = [
  { name: 'Home', href: '/', icon: PhHouse },
  { name: 'Bounties', href: '/bounties', icon: PhMagnifyingGlass },
  { name: 'Manifesto', href: '/manifesto', icon: PhScroll },
  // Add more links as needed
  // { name: 'My Deals', href: '/deals', icon: PhPaperPlaneTilt, requiresAuth: true },
];

const toggleTheme = () => {
  uiStore.toggleDarkMode();
};

// Close drawer on navigation for mobile
watch(() => useRoute().path, () => {
  drawer.value = false;
});
</script>

<style scoped lang="scss">
.app-header {
  // The glass-effect class from main.css will handle most of this
  // border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important; // Ensure Vuetify's border is overridden if needed
}

.v-toolbar-title {
  letter-spacing: 0.5px;
}

.v-btn--active {
  // color: #7F5AF0 !important; // Quantum Purple for active links
  // background-color: rgba(127, 90, 240, 0.1) !important;
}

// Custom styling for the drawer to match the glass theme
.v-navigation-drawer {
  border-left: 1px solid rgba(255, 255, 255, 0.1) !important;
}
</style>
