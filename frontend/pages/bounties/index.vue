<template>
  <div class="bounty-board-page container mx-auto py-8 px-4 md:px-0">
    <header class="mb-8 md:flex justify-between items-center">
      <div>
        <h1 class="text-4xl font-bold font-display text-pure-white mb-2">Bounty Board</h1>
        <p class="text-lg text-gray-400">Discover opportunities or find the perfect Connector.</p>
      </div>
      <AppButton to="/bounties/new" color="quantum-purple" size="medium" class="mt-4 md:mt-0">
        <PhPlusCircle class="mr-2" weight="bold" /> Post a New Bounty
      </AppButton>
    </header>

    <div class="flex flex-col md:flex-row gap-8">
      <!-- Filters Section -->
      <aside class="w-full md:w-1/4 lg:w-1/5">
        <GlassCard padding="p-4 md:p-6" class="sticky top-24"> <!-- top-24 to account for header height -->
          <template #header>
            <h2 class="text-xl font-semibold text-pure-white flex items-center">
              <PhFadersHorizontal class="mr-2 text-quantum-purple" weight="bold" /> Filters
            </h2>
          </template>
          <BountyFilters @filter-change="applyFilters" :active-filters="currentFilters" />
        </GlassCard>
      </aside>

      <!-- Bounties List Section -->
      <main class="w-full md:w-3/4 lg:w-4/5">
        <div v-if="pending && !bounties.length" class="text-center py-10">
          <UiAppLoader message="Fetching bounties..." />
        </div>
        <div v-else-if="error && !pending" class="text-center py-10">
          <GlassCard padding="p-6" class="max-w-md mx-auto">
            <PhWarningOctagon size="48" class="text-danger-red mx-auto mb-4" />
            <p class="text-lg text-gray-300">Could not load bounties.</p>
            <p class="text-sm text-danger-red/80 mt-1">{{ error.message || 'Please try again later.' }}</p>
            <AppButton @click="refreshBounties" color="quantum-purple" class="mt-6 mx-auto" size="small">
              <PhArrowClockwise class="mr-2" /> Try Again
            </AppButton>
          </GlassCard>
        </div>
        <div v-else-if="!bounties.length && !pending" class="text-center py-10">
            <GlassCard padding="p-8" class="max-w-lg mx-auto">
              <PhBinoculars size="64" class="text-quantum-purple/70 mx-auto mb-6" weight="duotone" />
              <h3 class="text-2xl font-semibold text-pure-white mb-3">No Bounties Found</h3>
              <p class="text-gray-400 mb-6">
                It seems there are no bounties matching your criteria right now.
                Why not <NuxtLink to="/bounties/new" class="text-quantum-purple hover:underline font-semibold">post one</NuxtLink>?
              </p>
              <AppButton v-if="hasActiveFilters" @click="clearAllFilters" color="quantum-purple" variant="outline" size="small">
                Clear All Filters
              </AppButton>
            </GlassCard>
        </div>
        <div v-else class="space-y-6">
          <BountyCard
            v-for="bounty in bounties"
            :key="bounty.id"
            :bounty="bounty"
            data-aos="fade-up"
            :data-aos-delay="bounties.indexOf(bounty) * 100"
          />
          <!-- Pagination (implement later if needed) -->
          <div v-if="pagination.totalPages > 1" class="mt-8 flex justify-center">
             <v-pagination
                v-model="pagination.currentPage"
                :length="pagination.totalPages"
                :total-visible="7"
                @update:modelValue="handlePageChange"
                active-color="quantum-purple"
                variant="elevated"
                density="comfortable"
              ></v-pagination>
          </div>
        </div>
         <div v-if="pending && bounties.length" class="mt-6">
            <UiAppLoader message="Loading more..." inline />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  PhPlusCircle, PhFadersHorizontal, PhBinoculars, PhWarningOctagon, PhArrowClockwise
} from 'phosphor-vue';
import AppButton from '~/components/ui/AppButton.vue';
import GlassCard from '~/components/ui/GlassCard.vue';
import UiAppLoader from '~/components/ui/AppLoader.vue';
import BountyCard from '~/components/bounty/BountyCard.vue';
import BountyFilters from '~/components/bounty/BountyFilters.vue';
import type { Bounty, BountyFilters as BountyFilterType } from '~/types'; // Assuming types are defined
import { useApiFetch } from '~/composables/useApiFetch';

definePageMeta({
  layout: 'default',
  // middleware: ['auth-only'], // Ensure user is authenticated to see bounties
});

useHead({
  title: 'Bounty Board - Access Marketplace',
  meta: [
    { name: 'description', content: 'Explore available bounties or find connectors for your needs.' }
  ],
});

const route = useRoute();
const router = useRouter();

const bounties = ref<Bounty[]>([]);
const currentFilters = reactive<BountyFilterType>({
  searchTerm: route.query.searchTerm as string || '',
  category: route.query.category as string || '',
  minAmount: route.query.minAmount ? parseInt(route.query.minAmount as string) : undefined,
  maxAmount: route.query.maxAmount ? parseInt(route.query.maxAmount as string) : undefined,
  status: (route.query.status as string) || 'open',
  sortBy: (route.query.sortBy as string) || 'created_at_desc',
});

const pagination = reactive({
  currentPage: route.query.page ? parseInt(route.query.page as string) : 1,
  pageSize: 10,
  totalItems: 0,
  totalPages: 0,
});

const buildQueryString = () => {
  const params = new URLSearchParams();
  if (currentFilters.searchTerm) params.append('searchTerm', currentFilters.searchTerm);
  if (currentFilters.category) params.append('category', currentFilters.category);
  if (currentFilters.minAmount) params.append('minAmount', String(currentFilters.minAmount));
  if (currentFilters.maxAmount) params.append('maxAmount', String(currentFilters.maxAmount));
  if (currentFilters.status) params.append('status', currentFilters.status);
  if (currentFilters.sortBy) params.append('sortBy', currentFilters.sortBy);
  params.append('page', String(pagination.currentPage));
  params.append('limit', String(pagination.pageSize));
  return params.toString();
};

const { data, pending, error, refresh: refreshBounties, execute: fetchBounties } = await useApiFetch<{ data: Bounty[], meta: any }>(
  `/bounties?${buildQueryString()}`, { immediate: false } // `immediate: false` to control execution
);

const loadBounties = async () => {
  const queryString = buildQueryString();
  // Update router query without navigation for bookmarkable URLs / refresh
  router.push({ path: '/bounties', query: { ...currentFilters, page: pagination.currentPage } });

  // How to update the path for useApiFetch if it's already initialized?
  // Option 1: Re-assign the composable (not ideal)
  // Option 2: Pass URL as a ref to useApiFetch (if it supports it)
  // Option 3: Use `execute` with a new URL (not directly supported by useFetch's execute)
  // Option 4: `refresh` should re-evaluate its URL if the URL is reactive.
  // Let's make the URL reactive for `useFetch` to work well with `refresh`.
  // This requires `useApiFetch` to accept a ref for the path or for us to manage the state that builds the path.
  // For now, we'll call `execute` which should use the latest state of `buildQueryString` if `useFetch` is set up reactively.
  // The `useFetch` in Nuxt 3 is reactive to its URL argument if it's a ref or computed.
  // Since we are not passing a ref URL to `useApiFetch` directly, we'll manage this by calling `execute` which re-runs the fetch.
  // A better approach might be to have `useApiFetch` accept a `ComputedRef<string>` for the path.
  // Given the current `useApiFetch`, we might need to re-initialize or make its path parameter reactive.
  // Let's assume `refreshBounties` will re-evaluate the URL if the state it depends on changed.
  // The simplest way with current `useApiFetch` is to call `execute` after path changes, but `useFetch` itself needs its URL to be reactive.

  // Re-fetching by constructing the full path again for `useFetch` inside `useApiFetch`:
  // This implies that `useApiFetch` would need to be called again, or its internal `useFetch` needs a reactive URL.
  // A common pattern is to make the URL a `computed` property and pass it to `useFetch`.
  // Let's try to make the path for `useApiFetch` reactive.
  // This is a limitation if `useApiFetch` doesn't take a reactive path.
  // For now, we'll rely on `refreshBounties` and ensure query params are updated.
  // The URL for `useFetch` is determined when `useApiFetch` is called.
  // To make this work, `useApiFetch` itself would need to be recalled or its path argument made reactive.
  // Let's assume `useApiFetch` is smart enough or we adapt it.
  // A pragmatic way: `key` option in `useFetch` can be used for reactivity.
  // Or, we can just call `fetchBounties` which is `execute`.
  // `useFetch` url can be a ref. If useApiFetch uses that, it's fine.

  // Let's adjust how we call useApiFetch.
  // For this to work, the URL for useFetch must be a `Ref<string>` or `ComputedRef<string>`.
  // We can't easily change `useApiFetch` now. So, we'll have to rely on query updates and hoping `refresh` works.
  // Or, manage `pending` and `error` manually if we call `useApiFetch` in a function.

  // A simpler approach for this page:
  // Call a function that internally uses `useApiFetch` and updates `bounties.value`.
  // This is what `refreshBounties` essentially does but its URL is fixed at init.
  // The `execute` method of `useFetch` re-runs the request with the *original* options.
  // This means we need to ensure the URL is dynamic.

  // Let's try updating query and then calling refresh.
  // The router push updates the URL. Then `refreshBounties` (if it re-reads route.query or similar) might work.
  // This is often a tricky part of using generic fetch composables.

  // A more robust way:
  // Define `fetchBountiesFunction` that calls `useApiFetch` with the dynamic URL.
  // This means `pending`, `error`, `data` would be local to that function's call.
  // We need them to be reactive at page level.

  // The `useFetch` composable itself can take a `ref` or `computed` for the URL.
  // If `useApiFetch` passes this through, then `refreshBounties` will use the new URL.
  // Assuming `useApiFetch` is set up this way (it should be for a good composable).

  // Let's assume `refreshBounties()` will use the latest query parameters from the URL due to router.push.
  // Or, more directly, if the URL for useFetch inside useApiFetch is computed based on reactive state.
  // The current `useApiFetch` takes a static path. This is a limitation.

  // Workaround: We will need to manually manage the data updates.
  // Or, make the path a reactive variable that is passed to useApiFetch.
  // Let's assume we will modify useApiFetch to accept a reactive path later.
  // For now, we will call `useApiFetch` inside `loadBounties` if it's simple.
  // This means pending/error are not directly from the page-level composable.
  // This is getting complex. Let's simplify.

  // Simplest for now: rely on `router.push` to change URL, then `window.location.reload()` or similar. Not ideal.
  // Or, use `watch` on `route.query` to call `refreshBounties`.

  // The `useFetch` composable IS reactive to its URL argument.
  // So if `useApiFetch` passes its `path` argument directly to `useFetch`, and we make `path` reactive, it works.
  // Our `useApiFetch` takes `path: string`. This is not reactive.
  // SOLUTION: We need to call `useApiFetch` inside a function that is called on filter/page change.

  // Let's redefine `pending` and `error` at page level and manage them.
  const pagePending = ref(false);
  const pageError = ref<any>(null);

  const fetchAndSetBounties = async () => {
    pagePending.value = true;
    pageError.value = null;
    const queryString = buildQueryString();
    try {
      const { data: fetchedData, error: fetchErr } = await useApiFetch<{ data: Bounty[], meta: any }>(`/bounties?${queryString}`);
      if (fetchErr.value) {
        throw fetchErr.value;
      }
      if (fetchedData.value) {
        bounties.value = fetchedData.value.data;
        pagination.totalItems = fetchedData.value.meta.total;
        pagination.totalPages = fetchedData.value.meta.last_page;
        pagination.currentPage = fetchedData.value.meta.current_page;
      } else {
        bounties.value = [];
        pagination.totalItems = 0;
        pagination.totalPages = 0;
      }
    } catch (e) {
      pageError.value = e;
      bounties.value = []; // Clear bounties on error
      // console.error("Failed to fetch bounties:", e);
      // uiStore.showToast('Failed to load bounties.', 'error');
    } finally {
      pagePending.value = false;
    }
  };


  // This watch will react to query changes (e.g. from browser back/forward)
  watch(() => route.query, async (newQuery) => {
    currentFilters.searchTerm = newQuery.searchTerm as string || '';
    currentFilters.category = newQuery.category as string || '';
    currentFilters.minAmount = newQuery.minAmount ? parseInt(newQuery.minAmount as string) : undefined;
    currentFilters.maxAmount = newQuery.maxAmount ? parseInt(newQuery.maxAmount as string) : undefined;
    currentFilters.status = newQuery.status as string || 'open';
    currentFilters.sortBy = newQuery.sortBy as string || 'created_at_desc';
    pagination.currentPage = newQuery.page ? parseInt(newQuery.page as string) : 1;
    await fetchAndSetBounties();
  }, { deep: true, immediate: true }); // Immediate to load on first visit

  const applyFilters = (newFilters: BountyFilterType) => {
    // Update currentFilters, then router.push will trigger the watch
    Object.assign(currentFilters, newFilters);
    pagination.currentPage = 1; // Reset to first page on filter change
    router.push({ path: '/bounties', query: { ...currentFilters, page: pagination.currentPage } });
  };

  const handlePageChange = (newPage: number) => {
    pagination.currentPage = newPage;
    router.push({ path: '/bounties', query: { ...currentFilters, page: newPage } });
  };

  const hasActiveFilters = computed(() => {
    return !!currentFilters.searchTerm || !!currentFilters.category || currentFilters.minAmount !== undefined || currentFilters.maxAmount !== undefined || currentFilters.status !== 'open' || currentFilters.sortBy !== 'created_at_desc';
  });

  const clearAllFilters = () => {
    currentFilters.searchTerm = '';
    currentFilters.category = '';
    currentFilters.minAmount = undefined;
    currentFilters.maxAmount = undefined;
    currentFilters.status = 'open';
    currentFilters.sortBy = 'created_at_desc';
    pagination.currentPage = 1;
    router.push({ path: '/bounties', query: { status: 'open', sortBy: 'created_at_desc', page: 1 } }); // Minimal query
  };


  // Expose pending and error for template (use pagePending and pageError)
  const pending = pagePending; // Shadowing the one from useApiFetch for template use
  const error = pageError; // Shadowing for template use

  // AOS init for cards (if used)
  onMounted(() => {
    if (process.client) {
      // AOS.init(); // If you decided to use AOS
    }
  });
</script>

<style scoped lang="scss">
// Add any specific styles for the bounty board page
.v-pagination .v-btn--active {
  background-color: var(--v-theme-primary) !important; // Ensure Vuetify pagination active color
  color: white !important;
}
</style>
