<template>
  <div class="new-bounty-page container mx-auto py-8 px-4 md:px-0">
    <header class="mb-8">
      <NuxtLink to="/bounties" class="text-sm text-quantum-purple hover:underline flex items-center mb-4">
        <PhArrowLeft class="mr-1" weight="bold" /> Back to Bounty Board
      </NuxtLink>
      <h1 class="text-4xl font-bold font-display text-pure-white">Post a New Bounty</h1>
      <p class="text-lg text-gray-400">Define your need and let Connectors find you.</p>
    </header>

    <GlassCard padding="p-6 md:p-8 lg:p-10">
      <BountyForm @submit-success="handleBountyPosted" />
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { PhArrowLeft } from 'phosphor-vue';
import GlassCard from '~/components/ui/GlassCard.vue';
import BountyForm from '~/components/bounty/BountyForm.vue';
import type { Bounty } from '~/types';
import { useUiStore } from '~/store/ui';

definePageMeta({
  layout: 'default',
  middleware: ['auth-only'], // Only authenticated users can post bounties
});

useHead({
  title: 'Post New Bounty - Access Marketplace',
});

const router = useRouter();
const uiStore = useUiStore();

const handleBountyPosted = (newBounty: Bounty) => {
  // uiStore.showToast('Bounty posted successfully!', 'success'); // Handled by Toaster
  router.push(`/bounties/${newBounty.id}`); // Navigate to the newly created bounty's detail page
};
</script>

<style scoped lang="scss">
// Specific styles for the new bounty page if any
</style>
