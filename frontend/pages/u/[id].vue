<template>
  <div class="user-profile-page container mx-auto py-8 px-4 md:px-0">
    <div v-if="pending && !userProfile" class="text-center py-20">
      <UiAppLoader message="Loading user profile..." />
    </div>
    <div v-else-if="error && !pending" class="text-center py-10">
      <GlassCard padding="p-8" class="max-w-lg mx-auto">
        <PhUserCircleSlash size="64" class="text-danger-red mx-auto mb-6" weight="duotone" />
        <h2 class="text-2xl font-semibold text-pure-white mb-3">Profile Not Found</h2>
        <p class="text-gray-400 mb-6">
          {{ error.statusCode === 404 ? "This user profile could not be found." : (error.message || "An error occurred.") }}
        </p>
        <AppButton to="/" color="quantum-purple" variant="outline" size="small">
          Return Home
        </AppButton>
      </GlassCard>
    </div>

    <div v-else-if="userProfile" class="profile-content">
      <GlassCard class="profile-header-card mb-8" padding="p-0">
        <div class="h-40 md:h-56 bg-gradient-to-r from-quantum-purple/70 to-purple-800/50 rounded-t-xl relative">
          <!-- Cover image can go here -->
          <div v-if="isOwnProfile" class="absolute top-4 right-4">
            <AppButton to="/settings/profile" size="small" variant="outline" color="pure-white" class="!border-pure-white/50 hover:!border-pure-white !text-xs">
              <PhPencilSimple class="mr-1.5" /> Edit Profile
            </AppButton>
          </div>
        </div>
        <div class="p-6 md:p-8 flex flex-col sm:flex-row items-center sm:items-end -mt-16 sm:-mt-20 relative z-10">
          <VAvatar
            :image="userProfile.profileImageUrl || undefined"
            size="120"
            class="border-4 border-obsidian-black shadow-lg bg-gray-700 text-pure-white text-3xl font-bold"
          >
            <span v-if="!userProfile.profileImageUrl">{{ getInitials(userProfile.displayName) }}</span>
          </VAvatar>
          <div class="sm:ml-6 mt-4 sm:mt-0 text-center sm:text-left">
            <h1 class="text-3xl md:text-4xl font-bold font-display text-pure-white">{{ userProfile.displayName }}</h1>
            <p class="text-gray-400 text-sm">Member since {{ dayjs(userProfile.createdAt).format('MMMM YYYY') }}</p>
            <div class="flex items-center justify-center sm:justify-start space-x-2 mt-1">
              <PhStar v-for="i in 5" :key="i" :weight="i <= (userProfile.reputationScore || 0) ? 'fill' : 'light'" class="text-yellow-400" size="18"/>
              <span class="text-xs text-gray-500">({{ (userProfile.reputationScore || 0).toFixed(1) }} average rating)</span>
            </div>
          </div>
        </div>
      </GlassCard>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- About Section -->
        <div class="md:col-span-2">
          <GlassCard class="mb-8">
            <template #header>
              <h2 class="text-xl font-semibold text-pure-white font-display">About {{ userProfile.displayName }}</h2>
            </template>
            <p v-if="userProfile.bio" class="text-gray-300 leading-relaxed whitespace-pre-line">{{ userProfile.bio }}</p>
            <p v-else class="text-gray-500 italic">This user hasn't added a bio yet.</p>

            <div v-if="userProfile.linkedinUrl || userProfile.twitterUrl || userProfile.websiteUrl" class="mt-6 pt-4 border-t border-white/10">
                <h3 class="text-md font-semibold text-gray-200 mb-2">Links:</h3>
                <div class="flex flex-wrap gap-3">
                    <a v-if="userProfile.linkedinUrl" :href="userProfile.linkedinUrl" target="_blank" rel="noopener noreferrer" class="text-quantum-purple hover:underline flex items-center text-sm">
                        <PhLinkedinLogo class="mr-1.5" size="18"/> LinkedIn
                    </a>
                     <a v-if="userProfile.twitterUrl" :href="userProfile.twitterUrl" target="_blank" rel="noopener noreferrer" class="text-quantum-purple hover:underline flex items-center text-sm">
                        <PhTwitterLogo class="mr-1.5" size="18"/> Twitter / X
                    </a>
                     <a v-if="userProfile.websiteUrl" :href="userProfile.websiteUrl" target="_blank" rel="noopener noreferrer" class="text-quantum-purple hover:underline flex items-center text-sm">
                        <PhLink class="mr-1.5" size="18"/> Website
                    </a>
                </div>
            </div>
          </GlassCard>

          <!-- User's Open Bounties (if seeker) or Successful Connections (if connector) -->
          <GlassCard>
            <template #header>
              <h2 class="text-xl font-semibold text-pure-white font-display">
                {{ userProfile.role === 'seeker' ? 'Open Bounties' : (userProfile.role === 'connector' ? 'Successful Connections' : 'Activity') }}
              </h2>
            </template>
            <div v-if="activityPending" class="text-center py-5">
              <UiAppLoader :message="`Loading ${userProfile.role === 'seeker' ? 'bounties' : 'connections'}...`" inline/>
            </div>
            <div v-else-if="userActivity.length === 0" class="text-gray-500 italic py-5 text-center">
              No {{ userProfile.role === 'seeker' ? 'open bounties' : (userProfile.role === 'connector' ? 'successful connections' : 'activity') }} to display currently.
            </div>
            <div v-else class="space-y-4">
              <!-- Example: Displaying bounties -->
              <div v-for="item in userActivity" :key="item.id" class="p-3 bg-obsidian-black/30 rounded-md border border-white/10 hover:border-quantum-purple/50 transition-colors">
                <NuxtLink :to="userProfile.role === 'seeker' ? `/bounties/${item.id}` : (item.bounty ? `/bounties/${item.bounty.id}` : '#')" class="block">
                  <h4 class="font-semibold text-pure-white group-hover:text-quantum-purple">{{ item.title || (item.bounty ? item.bounty.title : 'Connection Activity') }}</h4>
                  <p class="text-xs text-gray-400 mt-0.5">
                    <span v-if="item.amount">Amount: {{ formatCurrency(item.amount, item.currency) }} | </span>
                    Status: <span :class="statusColorClass(item.status)">{{ item.status }}</span>
                  </p>
                </NuxtLink>
              </div>
            </div>
          </GlassCard>
        </div>

        <!-- Stats & Reputation Sidebar -->
        <aside class="md:col-span-1 space-y-6">
          <GlassCard>
            <template #header>
              <h2 class="text-xl font-semibold text-pure-white font-display">Statistics</h2>
            </template>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-400">Role:</span>
                <span class="text-pure-white font-medium capitalize">{{ userProfile.role }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Bounties Posted:</span>
                <span class="text-pure-white font-medium">{{ userProfile.stats?.bountiesPosted || 0 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Connections Made:</span>
                <span class="text-pure-white font-medium">{{ userProfile.stats?.connectionsMade || 0 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Success Rate:</span>
                <span class="text-pure-white font-medium">{{ (userProfile.stats?.successRate || 0) * 100 }}%</span>
              </div>
            </div>
          </GlassCard>
          <!-- Testimonials/Reviews (Future Feature) -->
           <GlassCard v-if="userProfile.testimonials && userProfile.testimonials.length > 0">
                <template #header>
                    <h2 class="text-xl font-semibold text-pure-white font-display">Testimonials</h2>
                </template>
                <div class="space-y-4">
                    <div v-for="testimonial in userProfile.testimonials" :key="testimonial.id" class="p-3 bg-obsidian-black/20 rounded-md border border-white/5">
                        <p class="text-sm text-gray-300 italic">"{{ testimonial.text }}"</p>
                        <p class="text-xs text-gray-500 mt-1 text-right">- {{ testimonial.authorName }}</p>
                    </div>
                </div>
            </GlassCard>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import dayjs from 'dayjs';
import {
  PhUserCircleSlash, PhPencilSimple, PhStar, PhLinkedinLogo, PhTwitterLogo, PhLink
} from 'phosphor-vue';
import type { User, Bounty, Deal } from '~/types'; // Assuming User type includes role, bio, stats, etc.
import { useApiFetch } from '~/composables/useApiFetch';
import { useAuthStore } from '~/store/auth';
import UiAppLoader from '~/components/ui/AppLoader.vue';
import GlassCard from '~/components/ui/GlassCard.vue';
import AppButton from '~/components/ui/AppButton.vue';
import { VAvatar } from 'vuetify/components/VAvatar';


definePageMeta({
  layout: 'default',
});

const route = useRoute();
const userId = route.params.id as string;
const authStore = useAuthStore();

const userProfile = ref<User | null>(null);
const userActivity = ref<Array<Bounty | Deal>>([]); // For bounties or deals
const activityPending = ref(false);

const { data: fetchedUserProfile, pending, error, refresh } = await useApiFetch<User>(`/users/${userId}`);
watch(fetchedUserProfile, (newVal) => {
  userProfile.value = newVal;
  if (newVal) {
    fetchUserActivity(newVal);
  }
}, { immediate: true });


useHead(() => ({
  title: userProfile.value ? `${userProfile.value.displayName}'s Profile` : 'User Profile',
  meta: [
    { name: 'description', content: userProfile.value?.bio?.substring(0, 150) || 'View user profile on Access Marketplace.' }
  ],
}));

const isOwnProfile = computed(() => authStore.isAuthenticated && authStore.user?.id === userId);

const getInitials = (name: string) => {
  if (!name) return '?';
  const parts = name.split(' ');
  return parts.map(part => part[0]).join('').toUpperCase().substring(0, 2);
};

const formatCurrency = (amount?: number, currencyCode?: string) => {
  if (typeof amount !== 'number') return 'N/A';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: currencyCode || 'USD' }).format(amount);
};

const statusColorClass = (status?: string) => {
  if (!status) return 'bg-gray-600/20 text-gray-300';
  switch (status.toLowerCase()) {
    case 'open': return 'bg-guardian-green/20 text-guardian-green';
    case 'in_progress': case 'claimed': return 'bg-blue-500/20 text-blue-400';
    case 'completed': return 'bg-purple-500/20 text-purple-400';
    default: return 'bg-gray-600/20 text-gray-300';
  }
};


const fetchUserActivity = async (profile: User) => {
  activityPending.value = true;
  let endpoint = '';
  if (profile.role === 'seeker') {
    endpoint = `/users/${profile.id}/bounties?status=open`; // Fetch open bounties for seeker
  } else if (profile.role === 'connector') {
    endpoint = `/users/${profile.id}/deals?status=completed`; // Fetch completed deals for connector
  } else {
    activityPending.value = false;
    return; // No specific activity to fetch for other roles or if role undefined
  }

  try {
    const { data: activityData, error: activityError } = await useApiFetch<any[]>(endpoint); // Use `any[]` or more specific type
    if (activityError.value) throw activityError.value;
    userActivity.value = activityData.value || [];
  } catch (e) {
    console.error("Failed to fetch user activity:", e);
    userActivity.value = [];
  } finally {
    activityPending.value = false;
  }
};

</script>

<style scoped lang="scss">
.profile-header-card {
  // Custom styling for the header card if GlassCard defaults are not enough
}
</style>
