<template>
  <div class="bounty-detail-page container mx-auto py-8 px-4 md:px-0">
    <header class="mb-6">
      <NuxtLink to="/bounties" class="text-sm text-quantum-purple hover:underline flex items-center mb-4">
        <PhArrowLeft class="mr-1" weight="bold" /> Back to Bounty Board
      </NuxtLink>
    </header>

    <div v-if="pending && !bounty" class="text-center py-20">
      <UiAppLoader message="Loading bounty details..." />
    </div>
    <div v-else-if="error && !pending" class="text-center py-10">
      <GlassCard padding="p-8" class="max-w-lg mx-auto">
        <PhWarningOctagon size="64" class="text-danger-red mx-auto mb-6" weight="duotone" />
        <h2 class="text-2xl font-semibold text-pure-white mb-3">Bounty Not Found</h2>
        <p class="text-gray-400 mb-6">
          {{ error.statusCode === 404 ? "This bounty could not be found. It might have been removed or the link is incorrect." : (error.message || "An error occurred while fetching the bounty.") }}
        </p>
        <AppButton to="/bounties" color="quantum-purple" variant="outline" size="small">
          Return to Bounty Board
        </AppButton>
      </GlassCard>
    </div>

    <div v-else-if="bounty" class="bounty-content grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Main Bounty Info Section -->
      <div class="lg:col-span-2">
        <GlassCard padding="p-6 md:p-8">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h1 class="text-3xl md:text-4xl font-bold font-display text-pure-white mb-2">{{ bounty.title }}</h1>
              <div class="flex items-center text-sm text-gray-400 mb-1">
                <PhUserCircle class="mr-1.5 text-quantum-purple" weight="fill" size="18" />
                Posted by
                <NuxtLink :to="`/u/${bounty.creator?.id || 'unknown'}`" class="ml-1 text-quantum-purple hover:underline font-semibold">
                  {{ bounty.creator?.displayName || 'Anonymous Seeker' }}
                </NuxtLink>
              </div>
              <div class="flex items-center text-sm text-gray-400">
                <PhClock class="mr-1.5 text-quantum-purple" weight="fill" size="18" />
                Posted {{ timeAgo }}
              </div>
            </div>
            <span
              class="px-3 py-1 text-xs font-semibold rounded-full uppercase tracking-wider"
              :class="statusColorClass(bounty.status)"
            >
              {{ bounty.status }}
            </span>
          </div>

          <div class="my-6 border-t border-b border-white/10 py-4 flex flex-wrap gap-x-6 gap-y-3 text-sm">
            <div class="flex items-center text-pure-white">
              <PhCoins class="mr-2 text-guardian-green" weight="bold" size="20" />
              <span class="font-semibold text-lg">{{ formatCurrency(bounty.amount) }}</span>&nbsp;<span class="text-gray-400">Bounty</span>
            </div>
            <div v-if="bounty.category" class="flex items-center text-gray-300">
              <PhTag class="mr-2 text-quantum-purple/80" weight="bold" size="20" />
              {{ bounty.category?.name || bounty.category }}
            </div>
             <div class="flex items-center text-gray-300">
              <PhCalendarBlank class="mr-2 text-quantum-purple/80" weight="bold" size="20" />
              Expires: {{ bounty.expiresAt ? dayjs(bounty.expiresAt).format('MMM D, YYYY') : 'N/A' }}
            </div>
          </div>

          <h2 class="text-xl font-semibold text-pure-white mb-3 mt-6 font-display">Bounty Description</h2>
          <div class="prose prose-invert max-w-none text-gray-300 leading-relaxed" v-html="parsedDescription"></div>

          <div v-if="bounty.terms && bounty.terms.length > 0">
            <h2 class="text-xl font-semibold text-pure-white mb-3 mt-8 font-display">Specific Terms & Conditions</h2>
            <ul class="list-disc list-inside text-gray-300 space-y-1.5 pl-1">
              <li v-for="(term, index) in bounty.terms" :key="index">{{ term }}</li>
            </ul>
          </div>

           <!-- Edit/Delete buttons for bounty creator -->
          <div v-if="authStore.isAuthenticated && authStore.user?.id === bounty.creator?.id && bounty.status === 'open'" class="mt-8 pt-6 border-t border-white/10 flex space-x-3">
            <AppButton :to="`/bounties/${bounty.id}/edit`" color="quantum-purple" variant="outline" size="small">
              <PhPencilSimple class="mr-1.5" /> Edit Bounty
            </AppButton>
            <AppButton @click="showDeleteConfirm = true" color="danger-red" variant="ghost" size="small">
              <PhTrash class="mr-1.5" /> Delete Bounty
            </AppButton>
          </div>
        </GlassCard>
      </div>

      <!-- Sidebar: Actions / Claims -->
      <aside class="lg:col-span-1 space-y-6">
        <GlassCard padding="p-6">
          <template #header>
            <h2 class="text-xl font-semibold text-pure-white mb-0 font-display">Actions</h2>
          </template>
          <div v-if="!authStore.isAuthenticated" class="text-center">
            <p class="text-gray-400 mb-3 text-sm">You need to be logged in to interact with bounties.</p>
            <AppButton to="/auth/login" color="quantum-purple" block>Login to Participate</AppButton>
          </div>
          <div v-else-if="authStore.user?.id === bounty.creator?.id">
            <p class="text-gray-400 text-sm">You are the creator of this bounty.</p>
            <!-- Manage claims, view applicants etc. -->
            <AppButton v-if="bounty.status === 'open'" to="#claims" color="quantum-purple" variant="outline" block class="mt-3">
               <PhUsersThree class="mr-2" /> View Claims ({{ bounty.claimCount || 0 }})
            </AppButton>
          </div>
          <div v-else-if="bounty.status === 'open'">
            <AppButton @click="handleClaimBounty" color="guardian-green" block :loading="isClaiming" :disabled="isClaiming || hasUserClaimed">
              <PhPaperPlaneTilt class="mr-2" weight="bold" /> {{ hasUserClaimed ? 'Already Claimed' : 'Claim This Bounty' }}
            </AppButton>
            <p v-if="hasUserClaimed" class="text-xs text-guardian-green/80 mt-2 text-center">You have submitted a claim for this bounty. Check "My Claims" for status.</p>
            <p class="text-xs text-gray-500 mt-3 leading-relaxed">
              By claiming, you propose to fulfill the bounty requirements. The Seeker will review claims and may initiate a secure transaction.
            </p>
          </div>
          <div v-else>
            <p class="text-gray-400 text-sm text-center">This bounty is currently not open for claims (Status: {{ bounty.status }}).</p>
          </div>
        </GlassCard>

        <!-- Placeholder for Claims List (if creator or relevant) -->
        <GlassCard v-if="authStore.isAuthenticated && authStore.user?.id === bounty.creator?.id && bounty.status !== 'draft'" id="claims" padding="p-6">
            <template #header>
                <h2 class="text-xl font-semibold text-pure-white mb-0 font-display">Claims Received ({{ bounty.claimCount || 0 }})</h2>
            </template>
            <!-- TODO: Implement Claims List Component -->
            <div v-if="!claims.length && !claimsPending" class="text-gray-400 text-sm py-4 text-center">No claims yet.</div>
            <UiAppLoader v-if="claimsPending" message="Loading claims..." />
            <div v-else class="space-y-3">
                <div v-for="claim in claims" :key="claim.id" class="p-3 bg-obsidian-black/30 rounded-md border border-white/10">
                    <p class="text-sm text-pure-white font-semibold">Claim by {{ claim.connector?.displayName }}</p>
                    <p class="text-xs text-gray-400">{{ dayjs(claim.createdAt).fromNow() }}</p>
                    <!-- Action to view claim details / accept / reject -->
                </div>
            </div>
        </GlassCard>

      </aside>
    </div>

    <!-- Delete Confirmation Modal -->
    <VDialog v-model="showDeleteConfirm" max-width="450" content-class="glass-effect !rounded-xl">
        <VCard class="!bg-obsidian-black/80 !text-pure-white" :class="{'!border !border-danger-red/50': showDeleteConfirm}">
            <VCardTitle class="text-xl font-display !text-danger-red flex items-center">
                <PhWarning class="mr-2" size="24"/> Confirm Deletion
            </VCardTitle>
            <VCardText class="!text-gray-300">
                Are you sure you want to delete this bounty? This action cannot be undone.
            </VCardText>
            <VCardActions class="!p-4">
                <VSpacer />
                <AppButton @click="showDeleteConfirm = false" variant="text" size="small">Cancel</AppButton>
                <AppButton @click="confirmDeleteBounty" color="danger-red" :loading="isDeleting" size="small">
                    Delete Bounty
                </AppButton>
            </VCardActions>
        </VCard>
    </VDialog>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
dayjs.extend(relativeTime);

import {
  PhArrowLeft, PhUserCircle, PhClock, PhCoins, PhTag, PhCalendarBlank, PhPaperPlaneTilt,
  PhPencilSimple, PhTrash, PhWarningOctagon, PhUsersThree, PhWarning
} from 'phosphor-vue';
import type { Bounty, Claim } from '~/types';
import { useApiFetch } from '~/composables/useApiFetch';
import { useTimeAgo } from '~/composables/useTimeAgo';
import { useAuthStore } from '~/store/auth';
import { useUiStore } from '~/store/ui';
import UiAppLoader from '~/components/ui/AppLoader.vue';
import GlassCard from '~/components/ui/GlassCard.vue';
import AppButton from '~/components/ui/AppButton.vue';
// Vuetify components for dialog
import { VDialog, VCard, VCardTitle, VCardText, VCardActions, VSpacer } from 'vuetify/components';


definePageMeta({
  layout: 'default',
});

const route = useRoute();
const router = useRouter();
const bountyId = route.params.id as string;

const authStore = useAuthStore();
const uiStore = useUiStore();

const bounty = ref<Bounty | null>(null);
const claims = ref<Claim[]>([]); // For claims list
const claimsPending = ref(false); // For claims loading state
const isClaiming = ref(false);
const hasUserClaimed = ref(false); // Check if current user has already claimed
const showDeleteConfirm = ref(false);
const isDeleting = ref(false);

const { data: fetchedBounty, pending, error, refresh } = await useApiFetch<Bounty>(`/bounties/${bountyId}`);
watch(fetchedBounty, (newVal) => {
  bounty.value = newVal;
  if (newVal) {
    // Potentially fetch claims if user is creator
    if (authStore.isAuthenticated && authStore.user?.id === newVal.creator?.id) {
      fetchClaimsForBounty();
    }
    // Check if current user has claimed this bounty
    checkUserClaimStatus();
  }
}, { immediate: true });

useHead(() => ({
  title: bounty.value ? bounty.value.title : 'Bounty Details',
  meta: [
    { name: 'description', content: bounty.value ? bounty.value.description.substring(0, 150) : 'View bounty details.' }
  ],
}));

const timeAgo = useTimeAgo(computed(() => bounty.value?.createdAt));

const parsedDescription = computed(() => {
  if (bounty.value?.description) {
    // Ensure DOMPurify runs on the client side
    if (process.client) {
      return DOMPurify.sanitize(marked.parse(bounty.value.description) as string);
    }
    // For SSR, you might return a less processed version or handle it differently
    // For now, let's just return the marked output, assuming it's safe enough for this context
    // or that client-side hydration will correct it.
    return marked.parse(bounty.value.description);
  }
  return '';
});

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: bounty.value?.currency || 'USD' }).format(amount);
};

const statusColorClass = (status: string) => {
  switch (status?.toLowerCase()) {
    case 'open': return 'bg-guardian-green/20 text-guardian-green';
    case 'in progress':
    case 'claimed':
      return 'bg-blue-500/20 text-blue-400';
    case 'completed': return 'bg-purple-500/20 text-purple-400';
    case 'cancelled':
    case 'expired':
      return 'bg-gray-500/20 text-gray-400';
    default: return 'bg-gray-600/20 text-gray-300';
  }
};

const fetchClaimsForBounty = async () => {
    if (!bounty.value) return;
    claimsPending.value = true;
    try {
        const { data: fetchedClaims, error: claimsError } = await useApiFetch<Claim[]>(`/bounties/${bounty.value.id}/claims`);
        if (claimsError.value) throw claimsError.value;
        claims.value = fetchedClaims.value || [];
    } catch (e) {
        // console.error("Failed to fetch claims:", e);
        // uiStore.showToast("Could not load claims for this bounty.", "error");
    } finally {
        claimsPending.value = false;
    }
};

const checkUserClaimStatus = async () => {
    if (!authStore.isAuthenticated || !bounty.value) {
        hasUserClaimed.value = false;
        return;
    }
    // This endpoint would check if the current authenticated user has a claim on this bounty
    try {
        // Assuming an endpoint like /bounties/{id}/my-claim or similar
        // Or, if claims list for user is available, check against that.
        // For simplicity, if we had claims in bounty.value.claims (from a populated field)
        // hasUserClaimed.value = bounty.value.claims?.some(claim => claim.connectorId === authStore.user?.id);

        // Let's assume an endpoint that returns a boolean or a claim object if exists
        const { data: userClaim, error: claimCheckError } = await useApiFetch<{ claimed: boolean, claim_id?: string }>(`/bounties/${bounty.value.id}/check-claim`);
        if (claimCheckError.value) {
            // console.warn("Could not check user claim status:", claimCheckError.value.message);
            hasUserClaimed.value = false; // Default to false on error
            return;
        }
        hasUserClaimed.value = userClaim.value?.claimed || false;

    } catch (e) {
        // console.warn("Error checking user claim status:", e);
        hasUserClaimed.value = false;
    }
};


const handleClaimBounty = async () => {
  if (!authStore.isAuthenticated) {
    router.push('/auth/login?redirect=/bounties/' + bountyId);
    return;
  }
  if (!bounty.value || hasUserClaimed.value) return;

  isClaiming.value = true;
  try {
    // The body for claim might include a proposal message, etc.
    const { data: newClaim, error: claimError } = await useApiFetch<Claim>(`/bounties/${bounty.value.id}/claims`, {
      method: 'POST',
      body: {
        // proposalMessage: "I can help with this!" // Example
      }
    });

    if (claimError.value) throw claimError.value;

    if (newClaim.value) {
      // uiStore.showToast('Bounty claimed successfully!', 'success');
      hasUserClaimed.value = true; // Update UI
      // Potentially add to local claims list or refresh claims
      if (bounty.value && authStore.user?.id === bounty.value.creator?.id) {
        fetchClaimsForBounty(); // Refresh claims list if creator
      }
       // Optionally, navigate to a "my claims" page or show more info.
       // router.push(`/deals/${newClaim.value.dealId}`); // If a deal is created immediately
    }
  } catch (e: any) {
    // console.error('Failed to claim bounty:', e);
    // uiStore.showToast(e.message || 'Failed to claim bounty. Please try again.', 'error');
  } finally {
    isClaiming.value = false;
  }
};

const confirmDeleteBounty = async () => {
    if (!bounty.value) return;
    isDeleting.value = true;
    try {
        const { error: deleteError } = await useApiFetch(`/bounties/${bounty.value.id}`, {
            method: 'DELETE',
        });
        if (deleteError.value) throw deleteError.value;
        // uiStore.showToast('Bounty deleted successfully.', 'success');
        router.push('/bounties');
    } catch (e: any) {
        // console.error("Failed to delete bounty:", e);
        // uiStore.showToast(e.message || "Failed to delete bounty.", "error");
    } finally {
        isDeleting.value = false;
        showDeleteConfirm.value = false;
    }
};

onMounted(() => {
  // If bounty data is already fetched, check claim status
  if (bounty.value) {
    checkUserClaimStatus();
  }
});

</script>

<style lang="scss">
.prose-invert {
  // Tailwind typography plugin defaults for dark mode
  // You can customize these further if needed
  h1, h2, h3, h4, h5, h6 {
    @apply text-pure-white;
  }
  a {
    @apply text-quantum-purple hover:text-purple-400;
  }
  strong {
    @apply text-gray-200;
  }
  // Add more prose customizations here
  // Example: code blocks
  pre {
    @apply bg-obsidian-black/50 border border-white/10 p-4 rounded-md text-sm;
  }
  code {
     @apply text-purple-300;
  }
  code::before, code::after {
    content: "" !important; /* Remove backticks from inline code if prose adds them */
  }
  blockquote {
    @apply border-l-4 border-quantum-purple pl-4 text-gray-400 italic;
  }
}

// Style for Vuetify dialog if needed beyond its defaults
.v-dialog .v-card {
    // Ensure glass effect is applied if content-class isn't enough
}
</style>
