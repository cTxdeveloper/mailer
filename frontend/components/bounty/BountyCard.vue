<template>
  <GlassCard
    class="bounty-card group relative overflow-hidden transition-all duration-300 ease-in-out hover:shadow-glow-purple-md"
    :tiltEffect="true"
    padding="p-0"
    :border-color="isHovered ? 'border-quantum-purple/50' : 'border-white/10'"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <NuxtLink :to="`/bounties/${bounty.id}`" class="block p-5 md:p-6 h-full flex flex-col">
      <div class="flex justify-between items-start mb-3">
        <h3 class="text-lg md:text-xl font-semibold text-pure-white group-hover:text-quantum-purple transition-colors duration-200 pr-4 leading-tight">
          {{ bounty.title }}
        </h3>
        <span
          class="px-2.5 py-1 text-xs font-semibold rounded-full uppercase tracking-wider flex-shrink-0"
          :class="statusColorClass"
        >
          {{ bounty.status }}
        </span>
      </div>

      <p class="text-sm text-gray-400 mb-4 line-clamp-3 leading-relaxed flex-grow">
        {{ bounty.description }}
      </p>

      <div class="mt-auto">
        <div class="flex flex-wrap gap-x-4 gap-y-2 text-xs text-gray-400 mb-3">
          <div class="flex items-center" title="Bounty Amount">
            <PhCoins class="mr-1.5 text-guardian-green" weight="bold" size="16" />
            <span class="font-medium text-gray-200">{{ formatCurrency(bounty.amount) }}</span>
          </div>
          <div v-if="bounty.category" class="flex items-center" title="Category">
            <PhTag class="mr-1.5 text-quantum-purple/80" weight="bold" size="16" />
            <span class="text-gray-300">{{ bounty.category.name || bounty.category }}</span>
          </div>
          <div class="flex items-center" title="Posted Date">
            <PhClock class="mr-1.5 text-purple-400/80" weight="bold" size="16" />
            <span class="text-gray-300">{{ timeAgo }}</span>
          </div>
        </div>

        <div class="border-t border-white/10 pt-3 flex justify-between items-center">
          <div class="flex items-center">
            <VAvatar size="28" :image="bounty.creator?.profileImageUrl || undefined" class="mr-2 border border-white/20">
              <span v-if="!bounty.creator?.profileImageUrl" class="text-xs font-semibold text-pure-white bg-quantum-purple/50">
                {{ getInitials(bounty.creator?.displayName || 'U') }}
              </span>
            </VAvatar>
            <NuxtLink :to="`/u/${bounty.creator?.id || 'unknown'}`" class="text-xs text-gray-400 hover:text-quantum-purple hover:underline">
              {{ bounty.creator?.displayName || 'Anonymous Seeker' }}
            </NuxtLink>
          </div>
          <AppButton
            :to="`/bounties/${bounty.id}`"
            size="small"
            variant="ghost"
            color="quantum-purple"
            class="!px-3 !py-1.5 group-hover:!bg-quantum-purple/20"
            aria-label="View Bounty Details"
          >
            View Details <PhArrowRight class="ml-1.5 transition-transform duration-200 group-hover:translate-x-0.5" />
          </AppButton>
        </div>
      </div>
    </NuxtLink>
    <!-- Subtle animated gradient border on hover -->
    <div
      v-if="isHovered"
      class="absolute inset-0 border-2 border-transparent rounded-xl pointer-events-none animate-border-glow"
      :style="{ borderRadius: 'inherit' }"
    ></div>
  </GlassCard>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { PhCoins, PhTag, PhClock, PhArrowRight } from 'phosphor-vue';
import { VAvatar } from 'vuetify/components/VAvatar';
import type { Bounty } from '~/types';
import { useTimeAgo } from '~/composables/useTimeAgo';
import GlassCard from '~/components/ui/GlassCard.vue';
import AppButton from '~/components/ui/AppButton.vue';

const props = defineProps<{
  bounty: Bounty;
}>();

const isHovered = ref(false);
const timeAgo = useTimeAgo(props.bounty.createdAt);

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: props.bounty.currency || 'USD' }).format(amount);
};

const getInitials = (name: string) => {
  if (!name) return 'U';
  const parts = name.split(' ');
  if (parts.length > 1) {
    return parts[0][0].toUpperCase() + parts[parts.length - 1][0].toUpperCase();
  }
  return name[0].toUpperCase();
};

const statusColorClass = computed(() => {
  switch (props.bounty.status?.toLowerCase()) {
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
});
</script>

<style scoped lang="scss">
.bounty-card {
  // Base styling is handled by GlassCard and Tailwind classes
  // The tilt effect is enabled via prop on GlassCard
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

@keyframes borderGlow {
  0% { border-color: rgba(127, 90, 240, 0.3); box-shadow: 0 0 5px rgba(127, 90, 240, 0.2); }
  50% { border-color: rgba(127, 90, 240, 0.7); box-shadow: 0 0 15px 3px rgba(127, 90, 240, 0.4); }
  100% { border-color: rgba(127, 90, 240, 0.3); box-shadow: 0 0 5px rgba(127, 90, 240, 0.2); }
}

.animate-border-glow {
  animation: borderGlow 2s infinite ease-in-out;
}
</style>
