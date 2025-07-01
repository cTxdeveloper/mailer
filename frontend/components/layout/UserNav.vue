<template>
  <div v-if="authStore.isAuthenticated && authStore.user" class="user-nav">
    <v-menu offset-y nudge-bottom="10" transition="slide-y-transition">
      <template v-slot:activator="{ props }">
        <v-btn icon v-bind="props" class="ml-2">
          <v-avatar size="36" color="quantum-purple" class="cursor-pointer">
            <img
              v-if="authStore.user.profileImageUrl"
              :src="authStore.user.profileImageUrl"
              :alt="authStore.user.displayName || 'User Avatar'"
            />
            <span v-else class="text-pure-white font-semibold text-lg">
              {{ getInitials(authStore.user.displayName || authStore.user.email) }}
            </span>
          </v-avatar>
        </v-btn>
      </template>

      <v-list nav dense class="bg-obsidian-black/90 glass-effect !p-0 min-w-[220px]">
        <div class="px-4 py-3 border-b border-white/10">
          <p class="text-sm font-semibold text-pure-white truncate">{{ authStore.user.displayName || 'User' }}</p>
          <p class="text-xs text-gray-400 truncate">{{ authStore.user.email }}</p>
        </div>

        <v-list-item
          v-for="(item, i) in menuItems"
          :key="i"
          :to="item.to"
          link
          class="hover:bg-quantum-purple/20 group"
          @click="item.action ? item.action() : null"
        >
          <template v-slot:prepend>
            <component :is="item.icon" class="mr-3 text-quantum-purple group-hover:text-pure-white" size="20" />
          </template>
          <v-list-item-title class="text-gray-200 group-hover:text-pure-white text-sm font-medium">
            {{ item.title }}
          </v-list-item-title>
        </v-list-item>

        <div class="px-2 py-2 border-t border-white/10">
           <AppButton
            block
            size="small"
            variant="text"
            @click="handleLogout"
            class="!text-danger-red/80 hover:!text-danger-red hover:!bg-danger-red/10 w-full justify-start"
          >
            <PhSignOut size="20" class="mr-2" />
            Logout
          </AppButton>
        </div>
      </v-list>
    </v-menu>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '~/store/auth';
import { useUiStore } from '~/store/ui'; // For toast notifications
import { PhUserCircle, PhGear, PhPackage, PhSignOut, PhCreditCard, PhBell } from 'phosphor-vue';

const authStore = useAuthStore();
const uiStore = useUiStore();
const router = useRouter();

const getInitials = (name: string) => {
  if (!name) return 'U';
  const parts = name.split(' ');
  if (parts.length > 1) {
    return parts[0][0].toUpperCase() + parts[parts.length - 1][0].toUpperCase();
  }
  return name[0].toUpperCase();
};

const menuItems = computed(() => [
  { title: 'Dashboard', to: '/dashboard', icon: PhUserCircle },
  { title: 'My Bounties', to: '/bounties?filter=my', icon: PhPackage },
  // { title: 'My Claims', to: '/claims', icon: PhPaperPlaneTilt }, // Example
  { title: 'Notifications', to: '/notifications', icon: PhBell },
  { title: 'Profile Settings', to: '/settings/profile', icon: PhGear },
  { title: 'Billing', to: '/settings/billing', icon: PhCreditCard }, // Example
]);

const handleLogout = async () => {
  try {
    await authStore.logout();
    // Use vue-sonner for toast, assuming it's globally available or through uiStore
    // Example: uiStore.showToast('Logged out successfully', 'success');
    router.push('/');
  } catch (error) {
    console.error('Logout failed:', error);
    // Example: uiStore.showToast('Logout failed. Please try again.', 'error');
  }
};
</script>

<style scoped lang="scss">
.user-nav .v-list-item {
  min-height: 40px;
}

.user-nav .v-list-item-title {
  font-size: 0.9rem;
}

// Ensure the menu has the glass effect
.v-menu > .v-overlay__content > .v-card,
.v-menu > .v-overlay__content > .v-sheet,
.v-menu > .v-overlay__content > .v-list {
  @apply glass-effect;
  background-color: rgba(18, 18, 22, 0.85) !important; // Darker for better readability
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
}
</style>
