<template>
  <v-footer app padless color="transparent" class="app-footer mt-16 border-t border-white/10">
    <v-container class="py-8 md:py-12">
      <v-row justify="space-between" align="center">
        <v-col cols="12" md="auto" class="text-center md:text-left mb-4 md:mb-0">
          <div class="flex items-center justify-center md:justify-start mb-2">
            <img src="/nexus-logo-light.svg" alt="Access Marketplace Logo" class="h-7 w-auto mr-2">
            <span class="text-xl font-display font-bold text-pure-white">Access Marketplace</span>
          </div>
          <p class="text-sm text-gray-400">
            &copy; {{ new Date().getFullYear() }} The Access Marketplace. All rights reserved.
          </p>
          <p class="text-xs text-gray-500 mt-1">
            Confidence through Craftsmanship.
          </p>
        </v-col>

        <v-col cols="12" md="auto">
          <div class="flex flex-wrap justify-center md:justify-end space-x-4 sm:space-x-6">
            <NuxtLink to="/manifesto" class="footer-link">Manifesto</NuxtLink>
            <NuxtLink to="/privacy" class="footer-link">Privacy Policy</NuxtLink>
            <NuxtLink to="/terms" class="footer-link">Terms of Service</NuxtLink>
            <NuxtLink to="/contact" class="footer-link">Contact Us</NuxtLink>
            <!-- Add more links as needed -->
          </div>
        </v-col>
      </v-row>
      <v-row class="mt-6">
        <v-col class="text-center text-xs text-gray-600">
          <p>Built with <PhHeart weight="fill" class="inline text-quantum-purple" /> and passion for meaningful connections.</p>
          <p class="mt-1">This platform is a demonstration and does not process real financial transactions.</p>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script setup lang="ts">
import { PhHeart } from 'phosphor-vue';
// You can import other icons if needed for social media links, etc.
// import { PhGithubLogo, PhTwitterLogo, PhLinkedinLogo } from 'phosphor-vue';
</script>

<style scoped lang="scss">
.app-footer {
  background: linear-gradient(180deg, rgba(16, 16, 20, 0.8) 0%, rgba(16, 16, 20, 0.95) 100%);
  // backdrop-filter: blur(5px); // Subtle blur if desired
}

.footer-link {
  @apply text-gray-400 hover:text-quantum-purple transition-colors duration-200 text-sm;
  text-decoration: none;
}

// Example: Social media icons styling
.social-icon {
  @apply text-gray-500 hover:text-quantum-purple transition-colors duration-200;
}
</style>
