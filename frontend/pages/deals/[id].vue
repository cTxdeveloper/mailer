<template>
  <div class="deal-room-page container mx-auto py-8 px-4 md:px-0">
    <header class="mb-6 md:flex justify-between items-center">
      <div>
        <NuxtLink to="/dashboard" class="text-sm text-quantum-purple hover:underline flex items-center mb-2">
          <PhArrowLeft class="mr-1" weight="bold" /> Back to Dashboard
        </NuxtLink>
        <h1 class="text-3xl md:text-4xl font-bold font-display text-pure-white">
          Secure Deal Room
        </h1>
        <p v-if="deal" class="text-gray-400 text-lg">
          Regarding Bounty:
          <NuxtLink :to="`/bounties/${deal.bountyId}`" class="text-quantum-purple hover:underline">
            {{ deal.bounty?.title || 'View Bounty' }}
          </NuxtLink>
        </p>
      </div>
      <div v-if="deal" class="mt-4 md:mt-0 text-right">
        <span class="px-3 py-1.5 text-sm font-semibold rounded-full uppercase tracking-wider" :class="dealStatusColor(deal.status)">
          Status: {{ deal.status }}
        </span>
      </div>
    </header>

    <div v-if="pending && !deal" class="text-center py-20">
      <UiAppLoader message="Loading deal details..." />
    </div>
    <div v-else-if="error && !pending" class="text-center py-10">
      <GlassCard padding="p-8" class="max-w-lg mx-auto">
        <PhWarningOctagon size="64" class="text-danger-red mx-auto mb-6" weight="duotone" />
        <h2 class="text-2xl font-semibold text-pure-white mb-3">Deal Not Accessible</h2>
        <p class="text-gray-400 mb-6">
          {{ error.statusCode === 404 ? "This deal could not be found." : (error.message || "An error occurred.") }}
        </p>
        <AppButton to="/dashboard" color="quantum-purple" variant="outline" size="small">
          Return to Dashboard
        </AppButton>
      </GlassCard>
    </div>

    <div v-else-if="deal" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Deal Information & Actions Sidebar -->
      <aside class="lg:col-span-1 space-y-6 lg:sticky lg:top-24 self-start">
        <GlassCard padding="p-6">
          <template #header>
            <h2 class="text-xl font-semibold text-pure-white font-display">Deal Summary</h2>
          </template>
          <div class="space-y-3 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-400">Bounty Amount:</span>
              <span class="text-pure-white font-semibold">{{ formatCurrency(deal.bounty?.amount || 0, deal.bounty?.currency) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Seeker:</span>
              <NuxtLink :to="`/u/${deal.seekerId}`" class="text-quantum-purple hover:underline truncate">
                {{ deal.seeker?.displayName || 'Seeker' }}
              </NuxtLink>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Connector:</span>
              <NuxtLink :to="`/u/${deal.connectorId}`" class="text-quantum-purple hover:underline truncate">
                {{ deal.connector?.displayName || 'Connector' }}
              </NuxtLink>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Created:</span>
              <span class="text-gray-300">{{ dayjs(deal.createdAt).format('MMM D, YYYY') }}</span>
            </div>
          </div>

          <div class="mt-6 pt-4 border-t border-white/10">
            <NexusMascot :size="60" animationState="guarding" class="mx-auto my-3" />
            <p class="text-xs text-gray-400 text-center mb-3">
              Funds are currently <strong class="text-guardian-green">{{ deal.escrowStatus || 'Secured in Escrow' }}</strong>.
            </p>
            <!-- Action Buttons based on user role and deal status -->
            <div v-if="authStore.user?.id === deal.seekerId && deal.status === 'introduction_made'">
              <AppButton @click="releaseFunds" color="guardian-green" block :loading="actionPending">
                <PhChecks class="mr-2" /> Mark as Complete & Release Funds
              </AppButton>
            </div>
            <div v-else-if="authStore.user?.id === deal.connectorId && deal.status === 'escrow_funded'">
               <AppButton @click="markIntroMade" color="quantum-purple" block :loading="actionPending">
                <PhPaperPlaneRight class="mr-2" /> Mark Introduction as Made
              </AppButton>
            </div>
             <div v-else-if="deal.status === 'completed'">
                <p class="text-center text-guardian-green font-semibold"><PhCheckCircle class="inline mr-1"/> Deal Completed Successfully!</p>
            </div>
            <!-- TODO: Add dispute button/logic -->
            <AppButton v-if="deal.status !== 'completed' && deal.status !== 'cancelled'" @click="initiateDispute" color="danger-red" variant="text" block class="mt-3 !justify-start">
              <PhWarningOctagon class="mr-2" /> Raise a Dispute
            </AppButton>
          </div>
        </GlassCard>

        <!-- Visual Timeline -->
        <GlassCard padding="p-6">
            <template #header>
                <h2 class="text-xl font-semibold text-pure-white font-display mb-3">Deal Progress</h2>
            </template>
            <ul class="space-y-3">
                <li v-for="(step, index) in dealTimelineSteps" :key="step.name" class="flex items-center">
                    <div class="flex flex-col items-center mr-3">
                        <div class="w-6 h-6 rounded-full flex items-center justify-center"
                             :class="step.completed ? 'bg-guardian-green text-pure-white' : 'bg-gray-600 text-gray-300'">
                            <PhCheck v-if="step.completed" weight="bold" />
                            <span v-else class="text-xs font-bold">{{ index + 1 }}</span>
                        </div>
                        <div v-if="index < dealTimelineSteps.length - 1" class="w-px h-6" :class="step.completed ? 'bg-guardian-green' : 'bg-gray-600'"></div>
                    </div>
                    <div>
                        <p class="font-medium" :class="step.completed ? 'text-pure-white' : 'text-gray-400'">{{ step.name }}</p>
                        <p v-if="step.date" class="text-xs text-gray-500">{{ dayjs(step.date).format('MMM D, h:mma') }}</p>
                    </div>
                </li>
            </ul>
        </GlassCard>

      </aside>

      <!-- Chat Window Section -->
      <main class="lg:col-span-2">
        <DealChatWindow :deal-id="dealId" :deal="deal" @message-posted="refreshChatMessages" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import dayjs from 'dayjs';
import {
  PhArrowLeft, PhWarningOctagon, PhChecks, PhPaperPlaneRight, PhCheck, PhCheckCircle
} from 'phosphor-vue';
import type { Deal, DealStatus, User } from '~/types'; // Assuming types are defined
import { useApiFetch } from '~/composables/useApiFetch';
import { useAuthStore } from '~/store/auth';
import { useUiStore } from '~/store/ui';
import UiAppLoader from '~/components/ui/AppLoader.vue';
import GlassCard from '~/components/ui/GlassCard.vue';
import AppButton from '~/components/ui/AppButton.vue';
import DealChatWindow from '~/components/deal/DealChatWindow.vue';
import NexusMascot from '~/components/NexusMascot.vue';

definePageMeta({
  layout: 'default',
  middleware: ['auth-only'],
});

const route = useRoute();
const router = useRouter();
const dealId = route.params.id as string;

const authStore = useAuthStore();
const uiStore = useUiStore();

const deal = ref<Deal | null>(null);
const actionPending = ref(false); // For actions like releasing funds

const { data: fetchedDeal, pending, error, refresh: refreshDeal } = await useApiFetch<Deal>(`/deals/${dealId}`);
watch(fetchedDeal, (newVal) => {
  deal.value = newVal;
  // If deal includes bounty, seeker, connector objects, they will be populated.
  // Otherwise, you might need separate fetches or ensure backend populates them.
}, { immediate: true });

useHead(() => ({
  title: deal.value ? `Deal Room - ${deal.value.bounty?.title || `Deal #${deal.value.id}`}` : 'Deal Room',
}));

const formatCurrency = (amount: number, currencyCode?: string) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: currencyCode || 'USD' }).format(amount);
};

const dealStatusColor = (status?: DealStatus) => {
  if (!status) return 'bg-gray-600/20 text-gray-300';
  switch (status.toLowerCase()) {
    case 'pending_acceptance': return 'bg-yellow-500/20 text-yellow-400';
    case 'escrow_funded': return 'bg-blue-500/20 text-blue-400';
    case 'introduction_made': return 'bg-purple-500/20 text-purple-400';
    case 'completed': return 'bg-guardian-green/20 text-guardian-green';
    case 'disputed': return 'bg-danger-red/20 text-danger-red';
    case 'cancelled': return 'bg-gray-500/20 text-gray-400';
    default: return 'bg-gray-600/20 text-gray-300';
  }
};

const dealTimelineSteps = computed(() => {
    if (!deal.value) return [];
    const steps = [
        { name: 'Deal Initiated', date: deal.value.createdAt, completed: true }, // Always completed if deal exists
        { name: 'Escrow Funded', date: deal.value.escrowFundedAt, completed: !!deal.value.escrowFundedAt },
        { name: 'Introduction Made', date: deal.value.introductionMadeAt, completed: !!deal.value.introductionMadeAt },
        { name: 'Deal Completed', date: deal.value.completedAt, completed: !!deal.value.completedAt },
    ];
    if (deal.value.status === 'disputed' && deal.value.updatedAt) { // Using updatedAt for dispute time as an example
        steps.push({ name: 'Dispute Raised', date: deal.value.updatedAt, completed: true});
    }
    if (deal.value.status === 'cancelled' && deal.value.updatedAt) {
        steps.push({ name: 'Deal Cancelled', date: deal.value.updatedAt, completed: true});
    }
    // Sort by date just in case, though they should be chronological
    return steps.sort((a,b) => dayjs(a.date).valueOf() - dayjs(b.date).valueOf());
});


const releaseFunds = async () => {
  if (!deal.value) return;
  actionPending.value = true;
  try {
    const { error: releaseError } = await useApiFetch(`/deals/${deal.value.id}/release-escrow`, { method: 'POST' });
    if (releaseError.value) throw releaseError.value;
    // uiStore.showToast('Funds released successfully! Deal completed.', 'success');
    refreshDeal(); // Refresh deal details
  } catch (e: any) {
    // uiStore.showToast(e.message || 'Failed to release funds.', 'error');
  } finally {
    actionPending.value = false;
  }
};

const markIntroMade = async () => {
  if (!deal.value) return;
  actionPending.value = true;
  try {
    // This endpoint might require a message or proof.
    const { error: markError } = await useApiFetch(`/deals/${deal.value.id}/mark-introduction-made`, { method: 'POST' });
    if (markError.value) throw markError.value;
    // uiStore.showToast('Introduction marked as made. Seeker will be notified.', 'success');
    refreshDeal();
  } catch (e:any) {
    // uiStore.showToast(e.message || 'Failed to mark introduction.', 'error');
  } finally {
    actionPending.value = false;
  }
};

const initiateDispute = () => {
  if (!deal.value) return;
  // uiStore.showToast('Dispute process not yet implemented. Contact support.', 'info');
  // router.push(`/support/dispute?dealId=${deal.value.id}`);
  alert("Dispute process: Imagine a modal here to describe the issue, which then goes to admin review. For now, this is a placeholder.");
};


const refreshChatMessages = () => {
  // This function could be called by an event emitted from DealChatWindow
  // if it manages its own message fetching and needs to signal parent.
  // Or, if messages are part of the `deal` object, `refreshDeal()` would suffice.
  // For now, assume DealChatWindow handles its own message refresh or messages are part of deal.
  console.log("Chat message posted, potentially refresh deal or chat component state.");
};

</script>

<style scoped lang="scss">
.lg\:sticky {
  // Ensure sticky positioning works as expected with header
  // top value should be based on your fixed header's height + some padding
  // e.g., top: calc(var(--app-header-height, 64px) + 1rem);
}
</style>
