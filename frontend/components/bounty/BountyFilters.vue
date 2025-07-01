<template>
  <form @submit.prevent="submitFilters" class="space-y-6">
    <div>
      <label for="searchTerm" class="block text-sm font-medium text-gray-300 mb-1">Search Term</label>
      <UiFormInput
        id="searchTerm"
        name="searchTerm"
        v-model="filters.searchTerm"
        placeholder="Keywords, company, role..."
        :prepend-icon="PhMagnifyingGlass"
        @update:modelValue="debouncedSubmit"
        input-class="!py-2 !text-sm"
      />
    </div>

    <div>
      <label for="category" class="block text-sm font-medium text-gray-300 mb-1">Category</label>
      <VSelect
        id="category"
        v-model="filters.category"
        :items="categories"
        item-title="name"
        item-value="id"
        placeholder="Select category"
        variant="solo-filled"
        density="compact"
        clearable
        hide-details
        class="vuetify-select-custom"
        @update:modelValue="submitFilters"
      >
        <template v-slot:prepend-inner>
            <PhTag :size="20" class="mr-1 text-gray-400"/>
        </template>
      </VSelect>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-300 mb-1">Bounty Amount (USD)</label>
      <div class="flex space-x-2">
        <UiFormInput
          name="minAmount"
          type="number"
          v-model.number="filters.minAmount"
          placeholder="Min"
          :prepend-icon="PhCoinVertical"
          input-class="!py-2 !text-sm"
          @update:modelValue="debouncedSubmit"
        />
        <UiFormInput
          name="maxAmount"
          type="number"
          v-model.number="filters.maxAmount"
          placeholder="Max"
          :prepend-icon="PhCoinVertical"
          input-class="!py-2 !text-sm"
          @update:modelValue="debouncedSubmit"
        />
      </div>
    </div>

    <div>
      <label for="status" class="block text-sm font-medium text-gray-300 mb-1">Status</label>
       <VSelect
        id="status"
        v-model="filters.status"
        :items="statusOptions"
        placeholder="Any Status"
        variant="solo-filled"
        density="compact"
        clearable
        hide-details
        class="vuetify-select-custom"
        @update:modelValue="submitFilters"
      >
        <template v-slot:prepend-inner>
            <PhToggleLeft :size="20" class="mr-1 text-gray-400"/>
        </template>
      </VSelect>
    </div>

    <div>
      <label for="sortBy" class="block text-sm font-medium text-gray-300 mb-1">Sort By</label>
       <VSelect
        id="sortBy"
        v-model="filters.sortBy"
        :items="sortOptions"
        item-title="name"
        item-value="value"
        placeholder="Relevance"
        variant="solo-filled"
        density="compact"
        hide-details
        class="vuetify-select-custom"
        @update:modelValue="submitFilters"
      >
        <template v-slot:prepend-inner>
            <PhSortAscending :size="20" class="mr-1 text-gray-400"/>
        </template>
      </VSelect>
    </div>

    <div class="pt-2">
      <AppButton type="button" @click="clearFilters" variant="outline" color="pure-white" block size="small" class="!border-gray-500 hover:!border-pure-white">
        <PhEraser class="mr-2" /> Clear All Filters
      </AppButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue';
import { PhMagnifyingGlass, PhTag, PhCoinVertical, PhToggleLeft, PhSortAscending, PhEraser } from 'phosphor-vue';
import { VSelect } from 'vuetify/components/VSelect'; // Using Vuetify select for better UX
import UiFormInput from '~/components/ui/FormInput.vue'; // Assuming this is your custom input
import AppButton from '~/components/ui/AppButton.vue';
import type { BountyFilters, Category } from '~/types';
import { useApiFetch } from '~/composables/useApiFetch';
import { debounce } from 'lodash-es'; // Using lodash debounce

const props = defineProps<{
  activeFilters?: BountyFilters;
}>();

const emit = defineEmits(['filter-change']);

const filters = reactive<BountyFilters>({
  searchTerm: props.activeFilters?.searchTerm || '',
  category: props.activeFilters?.category || '',
  minAmount: props.activeFilters?.minAmount,
  maxAmount: props.activeFilters?.maxAmount,
  status: props.activeFilters?.status || 'open', // Default to 'open'
  sortBy: props.activeFilters?.sortBy || 'created_at_desc', // Default sort
});

const categories = ref<Category[]>([]); // To be fetched from API
// Example static categories if API is not ready
// const categories = ref([
//   { id: 'tech', name: 'Technology' },
//   { id: 'finance', name: 'Finance' },
//   { id: 'marketing', name: 'Marketing' },
//   { id: 'saas', name: 'SaaS' },
//   { id: 'web3', name: 'Web3/Crypto' },
// ]);

const statusOptions = ref([
  { title: 'Open', value: 'open' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Completed', value: 'completed' },
  { title: 'Expired', value: 'expired' },
  { title: 'Any Status', value: ''},
]);

const sortOptions = ref([
  { name: 'Newest First', value: 'created_at_desc' },
  { name: 'Oldest First', value: 'created_at_asc' },
  { name: 'Highest Bounty', value: 'amount_desc' },
  { name: 'Lowest Bounty', value: 'amount_asc' },
  // { name: 'Most Urgent', value: 'urgency_desc' }, // If urgency is a field
]);

// Fetch categories from API
const fetchCategories = async () => {
  try {
    const { data, error } = await useApiFetch<Category[]>('/categories'); // Assuming a /categories endpoint
    if (error.value) throw error.value;
    categories.value = data.value || [];
  } catch (e) {
    console.error("Failed to fetch categories:", e);
    // Use static categories as fallback or show error
  }
};

onMounted(() => {
  fetchCategories();
  // Initialize filters from props if they exist (e.g., from URL query params)
  if (props.activeFilters) {
    Object.assign(filters, props.activeFilters);
  }
});


const submitFilters = () => {
  // Create a plain object copy for emitting
  const filtersToEmit = JSON.parse(JSON.stringify(filters));
  emit('filter-change', filtersToEmit);
};

// Debounce submission for text inputs to avoid too many API calls
const debouncedSubmit = debounce(submitFilters, 500);

const clearFilters = () => {
  filters.searchTerm = '';
  filters.category = '';
  filters.minAmount = undefined;
  filters.maxAmount = undefined;
  filters.status = 'open'; // Reset to default
  filters.sortBy = 'created_at_desc'; // Reset to default
  submitFilters();
};

// Watch for changes in props.activeFilters to update local state if filters are controlled externally (e.g., URL query)
watch(() => props.activeFilters, (newVal) => {
  if (newVal) {
    Object.assign(filters, newVal);
  }
}, { deep: true });

</script>

<style lang="scss">
/* Custom styling for Vuetify components within this scope */
.vuetify-select-custom {
  .v-field {
    background-color: rgba(var(--v-theme-on-surface), 0.05) !important; // Match UiFormInput bg-obsidian-black/30
    border-radius: 0.375rem; // rounded-md
    box-shadow: none !important;
    border: 1px solid transparent !important; // Remove Vuetify's default border
     color: white; // Text color
  }
   .v-field:hover {
     border: 1px solid rgba(var(--v-theme-on-surface), 0.2)!important;
   }
  .v-field--focused {
    border: 1px solid rgb(var(--v-theme-primary)) !important; // Quantum Purple on focus
    box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.2) !important; // Ring effect
  }
  .v-field__input {
    padding-top: 8px !important; // Adjust padding to match UiFormInput
    padding-bottom: 8px !important;
    font-size: 0.875rem; // text-sm
     color: white !important;
  }
  .v-select__selection-text {
    color: white !important;
  }
  .v-label.v-field-label {
    color: #9ca3af !important; /* gray-400 for placeholder */
    font-size: 0.875rem;
  }
   .v-icon {
     color: #9ca3af !important; /* gray-400 for icons */
   }
    .v-field__prepend-inner .v-icon {
      margin-inline-end: 6px !important; // Reduce margin for prepend icon
    }

  // Ensure dropdown menu also has dark theme
  .v-overlay__content .v-list {
    background-color: #1E1E22 !important; // Dark surface color
    border: 1px solid rgba(255,255,255,0.1) !important;
    .v-list-item-title {
      color: #E0E0E0 !important; // Light text for items
    }
    .v-list-item--active > .v-list-item__overlay {
      background-color: rgb(var(--v-theme-primary)) !important; // Quantum purple for active
    }
     .v-list-item:hover > .v-list-item__overlay {
        background-color: rgba(var(--v-theme-primary), 0.2) !important;
     }
  }
}

// UiFormInput specific overrides if needed for filters context
// For example, making them smaller:
// :deep(.form-input-base) { /* If UiFormInput uses this class */
//   padding-top: 0.5rem;
//   padding-bottom: 0.5rem;
//   font-size: 0.875rem;
// }
</style>
