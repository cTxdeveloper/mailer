<template>
  <div class="dashboard-page container mx-auto py-8 px-4 md:px-0">
    <header class="mb-8">
      <h1 class="text-4xl font-bold font-display text-pure-white">Welcome, {{ authStore.user?.displayName || 'User' }}!</h1>
      <p class="text-lg text-gray-400">Here's an overview of your activity on The Access Marketplace.</p>
    </header>

    <div v-if="pending && !dashboardData" class="text-center py-20">
      <UiAppLoader message="Loading your dashboard..." />
    </div>
    <div v-else-if="error && !pending" class="text-center py-10">
       <GlassCard padding="p-6" class="max-w-md mx-auto">
        <PhWarningOctagon size="48" class="text-danger-red mx-auto mb-4" />
        <p class="text-lg text-gray-300">Could not load dashboard data.</p>
        <p class="text-sm text-danger-red/80 mt-1">{{ error.message || 'Please try again later.' }}</p>
        <AppButton @click="refresh" color="quantum-purple" class="mt-6 mx-auto" size="small">
          <PhArrowClockwise class="mr-2" /> Try Again
        </AppButton>
      </GlassCard>
    </div>

    <div v-else-if="dashboardData" class="dashboard-content">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <GlassCard class="text-center hover-lift" :interactiveGlow="true">
          <PhWallet size="36" class="text-quantum-purple mx-auto mb-3" weight="duotone" />
          <p class="text-xs text-gray-400 uppercase tracking-wider">Current Balance</p>
          <p class="text-2xl font-bold text-pure-white mt-1">{{ formatCurrency(dashboardData.walletBalance) }}</p>
        </GlassCard>
        <GlassCard class="text-center hover-lift" :interactiveGlow="true">
          <PhTarget size="36" class="text-guardian-green mx-auto mb-3" weight="duotone" />
          <p class="text-xs text-gray-400 uppercase tracking-wider">Active Bounties</p>
          <p class="text-2xl font-bold text-pure-white mt-1">{{ dashboardData.activeBountiesCount }}</p>
        </GlassCard>
        <GlassCard class="text-center hover-lift" :interactiveGlow="true">
          <PhPaperPlaneTilt size="36" class="text-blue-400 mx-auto mb-3" weight="duotone" />
          <p class="text-xs text-gray-400 uppercase tracking-wider">Active Claims/Deals</p>
          <p class="text-2xl font-bold text-pure-white mt-1">{{ dashboardData.activeDealsCount }}</p>
        </GlassCard>
        <GlassCard class="text-center hover-lift" :interactiveGlow="true">
          <PhStar size="36" class="text-yellow-400 mx-auto mb-3" weight="duotone" />
          <p class="text-xs text-gray-400 uppercase tracking-wider">Reputation Score</p>
          <p class="text-2xl font-bold text-pure-white mt-1">{{ (dashboardData.reputationScore || 0).toFixed(1) }}</p>
        </GlassCard>
      </div>

      <!-- Main Content Area: Recent Activity & Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Recent Activity -->
        <div class="lg:col-span-2">
          <GlassCard>
            <template #header>
              <h2 class="text-xl font-semibold text-pure-white font-display">Recent Activity</h2>
            </template>
            <div v-if="!dashboardData.recentActivity || dashboardData.recentActivity.length === 0" class="text-gray-500 italic py-5 text-center">
              No recent activity to display.
            </div>
            <ul v-else class="space-y-3">
              <li v-for="activity in dashboardData.recentActivity" :key="activity.id" class="p-3 bg-obsidian-black/20 rounded-md border border-white/10 flex items-center justify-between hover:border-quantum-purple/50 transition-colors">
                <div class="flex items-center">
                  <component :is="activityIcon(activity.type)" class="mr-3 flex-shrink-0 text-xl" :class="activityIconColor(activity.type)" weight="duotone" />
                  <div>
                    <p class="text-sm text-gray-200 leading-tight">{{ activity.description }}</p>
                    <p class="text-xs text-gray-500">{{ dayjs(activity.timestamp).fromNow() }}</p>
                  </div>
                </div>
                <NuxtLink v-if="activity.link" :to="activity.link" class="text-xs text-quantum-purple hover:underline">
                  View
                </NuxtLink>
              </li>
            </ul>
          </GlassCard>
        </div>

        <!-- Charts / Quick Actions -->
        <aside class="lg:col-span-1 space-y-6">
          <GlassCard>
            <template #header>
              <h2 class="text-xl font-semibold text-pure-white font-display">Earnings/Spending</h2>
            </template>
            <!-- ApexCharts will be mounted here by the plugin -->
            <ClientOnly>
              <apexchart type="area" height="250" :options="chartOptions" :series="chartSeries"></apexchart>
               <p v-if="!hasChartData" class="text-gray-500 text-sm text-center py-4">No financial data to display chart.</p>
            </ClientOnly>
          </GlassCard>

          <GlassCard>
            <template #header>
              <h2 class="text-xl font-semibold text-pure-white font-display">Quick Actions</h2>
            </template>
            <div class="space-y-3">
              <AppButton to="/bounties/new" color="quantum-purple" variant="outline" block>
                <PhPlusCircle class="mr-2" /> Post a New Bounty
              </AppButton>
              <AppButton to="/bounties" color="quantum-purple" variant="ghost" block>
                <PhMagnifyingGlass class="mr-2" /> Explore Bounties
              </AppButton>
              <AppButton to="/settings/profile" color="gray" variant="text" block class="!justify-start !text-gray-300 hover:!text-pure-white hover:!bg-white/5">
                <PhGearSix class="mr-2" /> Profile Settings
              </AppButton>
            </div>
          </GlassCard>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
dayjs.extend(relativeTime);

import {
  PhWallet, PhTarget, PhPaperPlaneTilt, PhStar, PhPlusCircle, PhMagnifyingGlass, PhGearSix,
  PhArrowUpRight, PhArrowDownLeft, PhHandshake, PhChatCircleText, PhWarningOctagon, PhArrowClockwise
} from 'phosphor-vue';
import type { User, Bounty, Deal, ActivityLog, DashboardData } from '~/types';
import { useAuthStore } from '~/store/auth';
import { useApiFetch } from '~/composables/useApiFetch';
import UiAppLoader from '~/components/ui/AppLoader.vue';
import GlassCard from '~/components/ui/GlassCard.vue';
import AppButton from '~/components/ui/AppButton.vue';
// ApexCharts is globally registered via plugin in nuxt.config.ts (plugins/apexcharts.client.js)

definePageMeta({
  layout: 'default',
  middleware: ['auth-only'],
});

useHead({
  title: 'Dashboard - Access Marketplace',
});

const authStore = useAuthStore();
const dashboardData = ref<DashboardData | null>(null);

const { data: fetchedData, pending, error, refresh } = await useApiFetch<DashboardData>('/dashboard'); // Assuming a /dashboard endpoint
watch(fetchedData, (newVal) => {
  dashboardData.value = newVal;
}, { immediate: true });


const formatCurrency = (amount?: number) => {
  if (typeof amount !== 'number') return '$0.00';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
};

const activityIcon = (type: string) => {
  switch (type?.toLowerCase()) {
    case 'bounty_posted': return PhTarget;
    case 'bounty_claimed': return PhHandshake;
    case 'deal_funded': return PhWallet;
    case 'intro_made': return PhPaperPlaneTilt;
    case 'deal_completed': return PhStar;
    case 'message_sent': return PhChatCircleText;
    case 'funds_added': return PhArrowUpRight;
    case 'payout_processed': return PhArrowDownLeft;
    default: return PhTarget;
  }
};
const activityIconColor = (type: string) => {
    switch (type?.toLowerCase()) {
    case 'bounty_posted': return 'text-quantum-purple';
    case 'bounty_claimed': return 'text-blue-400';
    case 'deal_funded': return 'text-guardian-green';
    case 'intro_made': return 'text-purple-400';
    case 'deal_completed': return 'text-yellow-400';
    case 'message_sent': return 'text-sky-400';
    case 'funds_added': return 'text-emerald-400';
    case 'payout_processed': return 'text-rose-400';
    default: return 'text-gray-400';
  }
}

const hasChartData = computed(() => {
    return dashboardData.value?.financialSummary?.series?.[0]?.data?.some(val => val > 0) ||
           dashboardData.value?.financialSummary?.series?.[1]?.data?.some(val => val > 0);
});

const chartOptions = computed(() => {
  const isDark = useUiStore().isDarkMode; // Assuming uiStore is accessible
  return {
    chart: {
      type: 'area',
      height: 250,
      foreColor: isDark ? '#E0E0E0' : '#373d3f',
      toolbar: { show: false },
      zoom: { enabled: false },
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800,
      }
    },
    colors: ['#2CB67D', '#7F5AF0'], // Guardian Green for Earnings, Quantum Purple for Spending
    dataLabels: { enabled: false },
    stroke: { curve: 'smooth', width: 2.5 },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.6,
        opacityTo: 0.1,
        stops: [0, 100]
      }
    },
    xaxis: {
      type: 'datetime',
      categories: dashboardData.value?.financialSummary?.categories || [],
      labels: {
        style: {
          colors: isDark ? '#9CA3AF' : '#6B7280', // gray-400 or gray-500
        },
        datetimeUTC: false,
      },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      labels: {
        style: {
          colors: isDark ? '#9CA3AF' : '#6B7280',
        },
        formatter: (value: number) => { return `$${value.toFixed(0)}` }
      },
    },
    legend: {
      position: 'top',
      horizontalAlign: 'right',
      offsetY: -5,
      markers: { radius: 12 },
      itemMargin: { horizontal: 10 },
    },
    grid: {
      borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
      strokeDashArray: 4,
      yaxis: { lines: { show: true } },
      xaxis: { lines: { show: false } },
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
      x: { format: 'MMM dd, yyyy' },
      y: { formatter: (value: number) => `$${value.toFixed(2)}` }
    },
  };
});

const chartSeries = computed(() => {
  return dashboardData.value?.financialSummary?.series || [
    { name: 'Earnings', data: [] },
    { name: 'Spending', data: [] },
  ];
});


// Example of how dashboardData might be structured in types/index.ts:
// export interface DashboardData {
//   walletBalance: number;
//   activeBountiesCount: number;
//   activeDealsCount: number;
//   reputationScore: number;
//   recentActivity: ActivityLog[];
//   financialSummary: {
//     categories: string[]; // Dates for x-axis
//     series: Array<{ name: string; data: number[] }>; // e.g., [{ name: 'Earnings', data: [...]}, { name: 'Spending', data: [...] }]
//   };
// }
// export interface ActivityLog {
//   id: string;
//   type: string; // e.g., 'bounty_posted', 'deal_completed'
//   description: string;
//   timestamp: string; // ISO date string
//   link?: string; // Optional link to relevant page
// }
</script>

<style scoped lang="scss">
.hover-lift {
  transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1), 0 0 15px rgba(127, 90, 240, 0.2); // Added purple glow
  }
}
// Ensure chart text colors adapt to theme if not handled by foreColor
:deep(.apexcharts-legend-text) {
  color: var(--v-theme-on-surface) !important; // Use Vuetify theme color
}
:deep(.apexcharts-tooltip-title) {
 color: var(--v-theme-on-surface) !important;
}
</style>
