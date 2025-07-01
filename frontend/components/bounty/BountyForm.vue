<template>
  <VeeForm @submit="submitBounty" :validation-schema="bountySchema" :initial-values="initialValues" v-slot="{ isSubmitting, errors: formErrors, setFieldValue, values }">
    <div class="space-y-6 md:space-y-8">
      <UiFormInput
        name="title"
        label="Bounty Title"
        placeholder="e.g., Introduction to Head of Engineering at Acme Corp"
        :prepend-icon="PhTextAlignLeft"
        hint="Be specific and clear. This is the first thing Connectors see."
        :disabled="isSubmitting"
      />

      <div>
        <label for="description" class="block text-sm font-medium text-gray-300 mb-1.5">
          Detailed Description
          <span class="text-danger-red">*</span>
        </label>
        <!-- Replace with a Rich Text Editor later if needed -->
        <UiFormTextarea
          name="description"
          label=""
          placeholder="Provide details about who you want to connect with, why, and any specific requirements for the introduction..."
          :rows="6"
          hint="Markdown is supported. Clearly outline the value proposition for the Connector."
          :disabled="isSubmitting"
        />
         <p class="mt-1 text-xs text-gray-400">Preview:</p>
        <div class="prose prose-sm prose-invert max-w-none p-3 border border-gray-700 rounded-md min-h-[50px] bg-obsidian-black/20 mt-1" v-html="previewDescription(values.description)"></div>
      </div>


      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <UiFormInput
          name="amount"
          type="number"
          label="Bounty Amount"
          placeholder="e.g., 500"
          :prepend-icon="PhCoins"
          hint="Amount in USD you're willing to pay for a successful introduction."
          :disabled="isSubmitting"
        >
          <template #append>
            <span class="text-gray-400 text-sm pr-3">USD</span>
          </template>
        </UiFormInput>

        <div>
          <label for="category" class="block text-sm font-medium text-gray-300 mb-1.5">Category</label>
          <VSelect
            name="category"
            v-model="selectedCategory"
            @update:modelValue="(value) => setFieldValue('categoryId', value)"
            :items="categories"
            item-title="name"
            item-value="id"
            placeholder="Select a relevant category"
            variant="solo-filled"
            density="comfortable"
            clearable
            class="vuetify-select-custom"
            :error-messages="formErrors.categoryId ? [formErrors.categoryId] : []"
            :disabled="isSubmitting"
          >
            <template v-slot:prepend-inner>
                <PhTag :size="20" class="mr-1 text-gray-400"/>
            </template>
          </VSelect>
          <VeeErrorMessage name="categoryId" class="mt-1.5 text-xs text-danger-red" />
        </div>
      </div>

      <div>
        <label for="terms" class="block text-sm font-medium text-gray-300 mb-1.5">
            Specific Terms or Conditions (Optional)
        </label>
        <div v-for="(term, index) in termsFields.fields.value" :key="term.key" class="flex items-center space-x-2 mb-2">
            <UiFormInput
                :name="`terms[${index}]`"
                placeholder="e.g., Must be a warm intro via email"
                class="flex-grow !mb-0"
                input-class="!py-2 !text-sm"
                :disabled="isSubmitting"
            />
            <AppButton type="button" @click="termsFields.remove(index)" variant="text" color="danger-red" size="small" class="!p-1.5" :disabled="isSubmitting">
                <PhXCircle size="20" />
            </AppButton>
        </div>
        <AppButton type="button" @click="termsFields.push('')" variant="outline" color="quantum-purple" size="small" :disabled="isSubmitting">
            <PhPlus class="mr-1"/> Add Term
        </AppButton>
      </div>


      <UiFormInput
        name="expiresAt"
        type="date"
        label="Expiration Date (Optional)"
        :prepend-icon="PhCalendarBlank"
        hint="When this bounty offer will expire. Leave blank for no expiration."
        :min="todayDate"
        :disabled="isSubmitting"
      />

      <div v-if="submissionError" class="bg-danger-red/10 p-3 rounded-md text-danger-red text-sm animate-fade-in">
        <PhWarningCircle weight="bold" class="inline mr-1" /> {{ submissionError }}
      </div>
       <div v-if="formErrors && Object.keys(formErrors).length > 0 && !submissionError && !Object.values(formErrors).every(e => !e)" class="bg-danger-red/10 p-3 rounded-md text-danger-red text-sm">
         Please correct the errors above.
      </div>


      <div class="pt-4 flex flex-col sm:flex-row justify-end space-y-3 sm:space-y-0 sm:space-x-4">
        <AppButton type="button" @click="cancelForm" variant="text" color="gray-400" :disabled="isSubmitting">
          Cancel
        </AppButton>
        <AppButton
          type="submit"
          :color="props.bounty ? 'guardian-green' : 'quantum-purple'"
          class="!py-3 text-base"
          :loading="isSubmitting"
          :disabled="isSubmitting"
        >
          <PhPaperPlaneTilt v-if="!props.bounty" class="mr-2" weight="bold" />
          <PhFloppyDisk v-else class="mr-2" weight="bold" />
          {{ props.bounty ? 'Save Changes' : 'Post Bounty' }}
        </AppButton>
      </div>
    </div>
  </VeeForm>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { object, string, number, array, date, mixed } from 'yup';
import { Form as VeeForm, FieldArray, ErrorMessage as VeeErrorMessage } from 'vee-validate';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

import {
  PhTextAlignLeft, PhCoins, PhTag, PhCalendarBlank, PhPaperPlaneTilt, PhFloppyDisk, PhPlus, PhXCircle, PhWarningCircle
} from 'phosphor-vue';
import { VSelect } from 'vuetify/components/VSelect';
import UiFormInput from '~/components/ui/FormInput.vue';
import UiFormTextarea from '~/components/ui/FormTextarea.vue';
import AppButton from '~/components/ui/AppButton.vue';
import type { Bounty, Category, BountyPayload } from '~/types';
import { useApiFetch } from '~/composables/useApiFetch';
import { useUiStore } from '~/store/ui';

const props = defineProps<{
  bounty?: Bounty | null; // For editing existing bounty
}>();

const emit = defineEmits(['submit-success', 'cancel']);

const router = useRouter();
const uiStore = useUiStore();

const categories = ref<Category[]>([]);
const selectedCategory = ref(props.bounty?.categoryId || ''); // For VSelect binding
const submissionError = ref<string | null>(null);

// For FieldArray
const termsFields = FieldArray<string>('terms');


const bountySchema = object({
  title: string().required('Title is required').max(150, 'Title is too long'),
  description: string().required('Description is required').min(50, 'Description is too short'),
  amount: number().required('Bounty amount is required').positive('Amount must be positive').min(1, 'Minimum bounty is $1'),
  categoryId: string().required('Category is required'), // Assuming category ID is a string
  terms: array().of(string().max(255, 'Term is too long')),
  expiresAt: date().nullable().min(new Date(), 'Expiration date cannot be in the past'),
});

const initialValues = computed(() => {
  if (props.bounty) {
    return {
      title: props.bounty.title,
      description: props.bounty.description,
      amount: props.bounty.amount,
      categoryId: props.bounty.categoryId, // This will be used by VeeValidate for the field
      terms: props.bounty.terms || [],
      expiresAt: props.bounty.expiresAt ? new Date(props.bounty.expiresAt).toISOString().split('T')[0] : null, // Format for date input
    };
  }
  return {
    terms: [''], // Start with one empty term field
  };
});

// Update selectedCategory when initialValues are set (for edit mode)
watch(initialValues, (newVals) => {
    if (newVals.categoryId) {
        selectedCategory.value = newVals.categoryId;
    }
}, { immediate: true });


const fetchCategories = async () => {
  try {
    const { data, error } = await useApiFetch<Category[]>('/categories');
    if (error.value) throw error.value;
    categories.value = data.value || [];
    // If editing and bounty has a category, ensure it's set for VSelect
    if (props.bounty?.categoryId && categories.value.find(c => c.id === props.bounty?.categoryId)) {
        selectedCategory.value = props.bounty.categoryId;
    }
  } catch (e) {
    console.error("Failed to fetch categories:", e);
    // uiStore.showToast('Could not load categories.', 'error');
  }
};

onMounted(() => {
  fetchCategories();
});

const previewDescription = (desc: string | undefined) => {
  if (!desc) return '<p class="text-gray-500"><em>Start typing to see a preview...</em></p>';
  if (process.client) {
    return DOMPurify.sanitize(marked.parse(desc) as string);
  }
  return marked.parse(desc);
};

const todayDate = computed(() => new Date().toISOString().split('T')[0]);

const submitBounty = async (values: any, { setErrors }) => {
  submissionError.value = null;

  const payload: BountyPayload = {
    title: values.title,
    description: values.description,
    amount: Number(values.amount),
    currency: 'USD', // Default for now, could be a form field
    category_id: values.categoryId, // Ensure backend expects snake_case if needed
    terms: values.terms?.filter((term: string) => term && term.trim() !== '') || [],
    expires_at: values.expiresAt || null, // Ensure backend expects snake_case
  };

  try {
    let response;
    if (props.bounty && props.bounty.id) {
      // Update existing bounty
      response = await useApiFetch<Bounty>(`/bounties/${props.bounty.id}`, {
        method: 'PUT',
        body: payload,
      });
    } else {
      // Create new bounty
      response = await useApiFetch<Bounty>('/bounties', {
        method: 'POST',
        body: payload,
      });
    }

    if (response.error.value) {
      if (response.error.value.data && response.error.value.data.errors) {
        const fieldErrors: Record<string, string> = {};
         for (const key in response.error.value.data.errors) {
            fieldErrors[key] = response.error.value.data.errors[key][0];
         }
        setErrors(fieldErrors);
        submissionError.value = response.error.value.message || "Please check the highlighted fields.";
      } else {
        submissionError.value = response.error.value.message || 'An unexpected error occurred.';
      }
      // uiStore.showToast(submissionError.value, 'error'); // Handled by Toaster
      return;
    }

    if (response.data.value) {
      // uiStore.showToast(props.bounty ? 'Bounty updated successfully!' : 'Bounty posted successfully!', 'success'); // Handled by Toaster
      emit('submit-success', response.data.value);
    }

  } catch (e: any) {
    // console.error('Submission error:', e);
    submissionError.value = 'A critical error occurred. Please try again.';
    // uiStore.showToast(submissionError.value, 'error'); // Handled by Toaster
  }
};

const cancelForm = () => {
  if (props.bounty) {
    router.push(`/bounties/${props.bounty.id}`);
  } else {
    router.push('/bounties');
  }
  emit('cancel');
};

</script>

<style lang="scss">
// Shared styles for Vuetify selects are in BountyFilters.vue or global.
// Ensure prose styles for markdown preview are loaded.
.prose-sm {
  font-size: 0.875rem;
  line-height: 1.5;
}
// Vuetify select custom styling is in BountyFilters.vue
// Ensure it's globally available or scoped here if needed.
.vuetify-select-custom {
  .v-field {
    background-color: rgba(var(--v-theme-on-surface), 0.05) !important;
    border-radius: 0.375rem;
    box-shadow: none !important;
    border: 1px solid transparent !important;
     color: white;
  }
   .v-field:hover {
     border: 1px solid rgba(var(--v-theme-on-surface), 0.2)!important;
   }
  .v-field--focused {
    border: 1px solid rgb(var(--v-theme-primary)) !important;
    box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.2) !important;
  }
  .v-field__input {
    padding-top: 10px !important; // Vuetify density="comfortable" default is 10px
    padding-bottom: 10px !important;
    font-size: 0.875rem;
     color: white !important;
  }
  .v-select__selection-text {
    color: white !important;
  }
  .v-label.v-field-label {
    color: #9ca3af !important;
    font-size: 0.875rem;
  }
   .v-icon {
     color: #9ca3af !important;
   }
   .v-field__prepend-inner .v-icon {
      margin-inline-end: 6px !important;
    }
  .v-overlay__content .v-list {
    background-color: #1E1E22 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    .v-list-item-title {
      color: #E0E0E0 !important;
    }
    .v-list-item--active > .v-list-item__overlay {
      background-color: rgb(var(--v-theme-primary)) !important;
    }
     .v-list-item:hover > .v-list-item__overlay {
        background-color: rgba(var(--v-theme-primary), 0.2) !important;
     }
  }
}
</style>
