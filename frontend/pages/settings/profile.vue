<template>
  <div class="profile-settings-page container mx-auto py-8 px-4 md:px-0">
    <header class="mb-8">
      <h1 class="text-3xl md:text-4xl font-bold font-display text-pure-white">Profile Settings</h1>
      <p class="text-lg text-gray-400">Manage your public presence and account details.</p>
    </header>

    <div v-if="pending && !authStore.user" class="text-center py-10">
        <UiAppLoader message="Loading your settings..." />
    </div>
    <div v-else-if="error && !pending" class="text-center py-10">
        <GlassCard padding="p-6" class="max-w-md mx-auto">
            <PhWarningOctagon size="48" class="text-danger-red mx-auto mb-4" />
            <p class="text-lg text-gray-300">Could not load your profile settings.</p>
            <p class="text-sm text-danger-red/80 mt-1">{{ error.message || 'Please try again later.' }}</p>
            <AppButton @click="refreshProfile" color="quantum-purple" class="mt-6 mx-auto" size="small">
              <PhArrowClockwise class="mr-2" /> Try Again
            </AppButton>
          </GlassCard>
    </div>
    <div v-else-if="authStore.user">
      <VeeForm @submit="updateProfile" :validation-schema="profileSchema" :initial-values="initialFormValues" v-slot="{ isSubmitting, errors: formErrors, setFieldValue }">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Left Column: Avatar and Basic Info -->
          <div class="md:col-span-1 space-y-6">
            <GlassCard>
              <template #header>
                <h2 class="text-xl font-semibold text-pure-white font-display">Profile Picture</h2>
              </template>
              <div class="flex flex-col items-center">
                <VAvatar
                  :image="previewImageUrl || authStore.user.profileImageUrl || undefined"
                  size="120"
                  class="mb-4 border-4 border-obsidian-black/30 shadow-lg bg-gray-700 text-pure-white text-3xl font-bold"
                >
                  <span v-if="!previewImageUrl && !authStore.user.profileImageUrl">{{ getInitials(authStore.user.displayName || authStore.user.email) }}</span>
                </VAvatar>
                <input type="file" @change="onFileChange" ref="fileInputRef" class="hidden" accept="image/*">
                <AppButton type="button" @click="triggerFileInput" variant="outline" color="quantum-purple" size="small">
                  <PhUploadSimple class="mr-1.5" /> Change Picture
                </AppButton>
                <p v-if="fileError" class="text-xs text-danger-red mt-2">{{ fileError }}</p>
                <p class="text-xs text-gray-500 mt-2">Max 2MB. JPG, PNG, GIF.</p>
              </div>
            </GlassCard>

            <GlassCard>
                <template #header><h2 class="text-xl font-semibold text-pure-white font-display">Account Role</h2></template>
                <p class="text-gray-300">Your current role is: <strong class="capitalize text-quantum-purple">{{ authStore.user.role }}</strong>.</p>
                <p class="text-xs text-gray-500 mt-1">Role changes are handled by support.</p>
            </GlassCard>
          </div>

          <!-- Right Column: Form Fields -->
          <div class="md:col-span-2">
            <GlassCard padding="p-6 md:p-8">
              <div class="space-y-6">
                <UiFormInput
                  name="displayName"
                  label="Display Name / Alias"
                  placeholder="Your public name"
                  :prepend-icon="PhUser"
                  :disabled="isSubmitting"
                />
                <UiFormInput
                  name="email"
                  type="email"
                  label="Email Address"
                  placeholder="your.email@example.com"
                  :prepend-icon="PhEnvelopeSimple"
                  disabled   мъ
                  hint="Email cannot be changed here. Contact support if needed."
                />
                <UiFormTextarea
                  name="bio"
                  label="Bio / About Me"
                  placeholder="Tell others about yourself, your expertise, and what you're looking for or offering."
                  :rows="5"
                  :disabled="isSubmitting"
                  maxLength="500"
                  showCharCount
                />

                <h3 class="text-lg font-semibold text-gray-200 pt-4 border-t border-white/10">Social & Website Links</h3>
                 <UiFormInput
                  name="linkedinUrl"
                  label="LinkedIn Profile URL (Optional)"
                  placeholder="https://linkedin.com/in/yourprofile"
                  :prepend-icon="PhLinkedinLogo"
                  :disabled="isSubmitting"
                />
                 <UiFormInput
                  name="twitterUrl"
                  label="Twitter / X Profile URL (Optional)"
                  placeholder="https://twitter.com/yourhandle"
                  :prepend-icon="PhTwitterLogo"
                  :disabled="isSubmitting"
                />
                 <UiFormInput
                  name="websiteUrl"
                  label="Personal/Company Website URL (Optional)"
                  placeholder="https://yourwebsite.com"
                  :prepend-icon="PhLink"
                  :disabled="isSubmitting"
                />

                <div v-if="updateError" class="bg-danger-red/10 p-3 rounded-md text-danger-red text-sm animate-fade-in">
                  <PhWarningCircle weight="bold" class="inline mr-1" /> {{ updateError }}
                </div>
                <div v-if="formErrors && Object.keys(formErrors).length > 0 && !updateError && !Object.values(formErrors).every(e => !e)" class="bg-danger-red/10 p-3 rounded-md text-danger-red text-sm">
                  Please correct the errors above.
                </div>

                <div class="flex justify-end pt-4 border-t border-white/10">
                  <AppButton type="submit" color="guardian-green" :loading="isSubmitting" :disabled="isSubmitting">
                    <PhFloppyDisk class="mr-2" /> Save Changes
                  </AppButton>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>
      </VeeForm>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { object, string, url } from 'yup';
import { Form as VeeForm } from 'vee-validate';
import {
  PhUser, PhEnvelopeSimple, PhLinkedinLogo, PhTwitterLogo, PhLink, PhUploadSimple, PhFloppyDisk, PhWarningOctagon, PhWarningCircle, PhArrowClockwise
} from 'phosphor-vue';
import { useAuthStore } from '~/store/auth';
import { useUiStore } from '~/store/ui';
import { useApiFetch } from '~/composables/useApiFetch';
import type { UserUpdatePayload, User } from '~/types';
import UiAppLoader from '~/components/ui/AppLoader.vue';
import GlassCard from '~/components/ui/GlassCard.vue';
import UiFormInput from '~/components/ui/FormInput.vue';
import UiFormTextarea from '~/components/ui/FormTextarea.vue';
import AppButton from '~/components/ui/AppButton.vue';
import { VAvatar } from 'vuetify/components/VAvatar';

definePageMeta({
  layout: 'default',
  middleware: ['auth-only'],
});

useHead({
  title: 'Profile Settings - Access Marketplace',
});

const authStore = useAuthStore();
const uiStore = useUiStore();

const updateError = ref<string | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const previewImageUrl = ref<string | null>(null);
const fileError = ref<string | null>(null);

// Use a local pending/error for initial profile load if authStore.user might not be populated yet
const pending = ref(false);
const error = ref<any>(null);

const profileSchema = object({
  displayName: string().required('Display name is required').min(3).max(50),
  email: string().email().required(), // Disabled, so validation won't block submit, but good to have
  bio: string().nullable().max(500, 'Bio cannot exceed 500 characters.'),
  linkedinUrl: url().nullable().label('LinkedIn URL'),
  twitterUrl: url().nullable().label('Twitter / X URL'),
  websiteUrl: url().nullable().label('Website URL'),
});

const initialFormValues = computed(() => {
  if (authStore.user) {
    return {
      displayName: authStore.user.displayName || '',
      email: authStore.user.email, // This field is disabled anyway
      bio: authStore.user.bio || '',
      linkedinUrl: authStore.user.linkedinUrl || '',
      twitterUrl: authStore.user.twitterUrl || '',
      websiteUrl: authStore.user.websiteUrl || '',
    };
  }
  return {};
});

const getInitials = (name?: string) => {
  if (!name) return '?';
  const parts = name.split(' ');
  return parts.map(part => part[0]).join('').toUpperCase().substring(0, 2);
};

const triggerFileInput = () => {
  fileInputRef.value?.click();
};

const onFileChange = (event: Event) => {
  fileError.value = null;
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    // Validate file type and size
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
      fileError.value = 'Invalid file type. Please use JPG, PNG, or GIF.';
      return;
    }
    if (file.size > 2 * 1024 * 1024) { // 2MB limit
      fileError.value = 'File is too large. Maximum size is 2MB.';
      return;
    }
    selectedFile.value = file;
    previewImageUrl.value = URL.createObjectURL(file);
  }
};

const updateProfile = async (values: any, { setErrors }) => {
  updateError.value = null;
  if (!authStore.user) return;

  const payload: UserUpdatePayload = {
    display_name: values.displayName,
    bio: values.bio,
    linkedin_url: values.linkedinUrl,
    twitter_url: values.twitterUrl,
    website_url: values.websiteUrl,
  };

  // If a new file is selected, upload it first or include it in the payload
  if (selectedFile.value) {
    const formData = new FormData();
    formData.append('profile_image', selectedFile.value);
    // Append other fields to FormData if backend expects multipart/form-data for all
    // Or, make a separate request for image upload.
    // For simplicity, assuming a separate endpoint for avatar or backend handles mixed content.
    // Here, we'll try to upload avatar first, then update text fields.

    try {
      // uiStore.showToast('Uploading profile picture...', 'info', { duration: 2000 }); // Handled by Toaster
      const { data: avatarData, error: avatarError } = await useApiFetch<{ profileImageUrl: string }>(`/users/me/avatar`, {
        method: 'POST',
        body: formData, // FormData will set Content-Type to multipart/form-data
      });
      if (avatarError.value) throw avatarError.value; // Handle avatar upload error

      if (avatarData.value?.profileImageUrl) {
        authStore.updateUserProfile({ profileImageUrl: avatarData.value.profileImageUrl });
        previewImageUrl.value = null; // Clear preview after successful upload
        selectedFile.value = null;
         // uiStore.showToast('Profile picture updated!', 'success'); // Handled by Toaster
      }
    } catch (e: any) {
      updateError.value = e.message || "Failed to upload profile picture.";
      // uiStore.showToast(updateError.value, 'error'); // Handled by Toaster
      // Decide if you want to stop profile update or continue with text fields
      // For now, we'll stop if avatar upload fails.
      return;
    }
  }

  // Update text fields
  try {
    const { data: updatedUser, error: updateApiError } = await useApiFetch<User>(`/users/me`, {
      method: 'PUT',
      body: payload,
    });

    if (updateApiError.value) {
       if (updateApiError.value.data && updateApiError.value.data.errors) {
        const fieldErrors: Record<string, string> = {};
         for (const key in updateApiError.value.data.errors) {
            fieldErrors[key] = updateApiError.value.data.errors[key][0];
         }
        setErrors(fieldErrors);
        updateError.value = updateApiError.value.message || "Please check the highlighted fields.";
      } else {
        updateError.value = updateApiError.value.message || 'An unexpected error occurred.';
      }
      // uiStore.showToast(updateError.value, 'error'); // Handled by Toaster
      return;
    }

    if (updatedUser.value) {
      authStore.updateUserProfile(updatedUser.value); // Update Pinia store
      // uiStore.showToast('Profile updated successfully!', 'success'); // Handled by Toaster
    }
  } catch (e: any) {
    updateError.value = 'A critical error occurred while updating profile.';
    // uiStore.showToast(updateError.value, 'error'); // Handled by Toaster
  }
};

// Fetch user data if not already present (e.g., on page refresh)
const refreshProfile = async () => {
    pending.value = true;
    error.value = null;
    try {
        await authStore.fetchUser(); // This should repopulate authStore.user
        if (!authStore.user) throw new Error("Failed to fetch user data.");
    } catch (e:any) {
        error.value = e;
    } finally {
        pending.value = false;
    }
};

onMounted(() => {
    if (!authStore.user) {
        refreshProfile();
    }
});

</script>

<style scoped lang="scss">
// Custom styles for profile settings if needed
</style>
