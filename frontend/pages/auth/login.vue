<template>
  <div class="auth-page-container min-h-screen flex items-center justify-center bg-gradient-to-br from-obsidian-black via-purple-900/30 to-obsidian-black p-4">
    <GlassCard class="w-full max-w-md shadow-2xl" :interactiveGlow="true" padding="p-6 md:p-10">
      <template #header>
        <div class="text-center">
          <NuxtLink to="/" class="inline-block mb-6">
            <img src="/nexus-logo-light.svg" alt="Access Marketplace Logo" class="h-12 w-auto">
          </NuxtLink>
          <h2 class="text-3xl font-bold font-display text-pure-white">Welcome Back</h2>
          <p class="text-gray-400 mt-2">Login to access your network.</p>
        </div>
      </template>

      <VeeForm @submit="handleLogin" :validation-schema="loginSchema" v-slot="{ isSubmitting, errors: formErrors }">
        <div class="space-y-5">
          <UiFormInput
            name="email"
            type="email"
            label="Email Address"
            placeholder="you@example.com"
            :prepend-icon="PhEnvelopeSimple"
            autocomplete="email"
            :disabled="isSubmitting"
          />
          <UiFormInput
            name="password"
            type="password"
            label="Password"
            placeholder="Enter your password"
            :prepend-icon="PhLockSimple"
            autocomplete="current-password"
            :disabled="isSubmitting"
          />

          <div v-if="loginError" class="bg-danger-red/10 p-3 rounded-md text-danger-red text-sm animate-fade-in">
            <PhWarningCircle weight="bold" class="inline mr-1" /> {{ loginError }}
          </div>
          <!-- Display form-level errors from VeeValidate if any (e.g., related to schema but not specific fields) -->
           <div v-if="formErrors && Object.keys(formErrors).length > 0 && !loginError" class="bg-danger-red/10 p-3 rounded-md text-danger-red text-sm">
            Please correct the highlighted errors.
          </div>


          <div class="flex items-center justify-between text-sm">
            <VeeField name="remember" type="checkbox" v-slot="{ field }">
              <label class="flex items-center text-gray-400 cursor-pointer">
                <input type="checkbox" v-bind="field" :value="true" class="h-4 w-4 text-quantum-purple bg-gray-700 border-gray-600 rounded focus:ring-quantum-purple mr-2" />
                Remember me
              </label>
            </VeeField>
            <NuxtLink to="/auth/forgot-password" class="font-medium text-quantum-purple hover:text-purple-400">
              Forgot password?
            </NuxtLink>
          </div>

          <AppButton
            type="submit"
            color="quantum-purple"
            class="w-full !py-3 text-base"
            :loading="isSubmitting"
            :disabled="isSubmitting"
          >
            <PhSignIn class="mr-2" weight="bold" />
            Login
          </AppButton>
        </div>
      </VeeForm>

      <template #footer>
        <p class="text-center text-sm text-gray-400">
          Don't have an account?
          <NuxtLink to="/auth/register" class="font-medium text-quantum-purple hover:text-purple-400">
            Sign up here
          </NuxtLink>
        </p>
      </template>
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '~/store/auth';
import { useUiStore } from '~/store/ui';
import { object, string, boolean } from 'yup';
import { PhEnvelopeSimple, PhLockSimple, PhSignIn, PhWarningCircle } from 'phosphor-vue';
import GlassCard from '~/components/ui/GlassCard.vue';
import UiFormInput from '~/components/ui/FormInput.vue';
import AppButton from '~/components/ui/AppButton.vue';
import { Form as VeeForm, Field as VeeField } from 'vee-validate'; // Import VeeValidate components

definePageMeta({
  layout: 'landing', // Use a minimal layout, or create an 'auth' layout
  middleware: ['guest-only'], // Redirect if already authenticated
});

useHead({
  title: 'Login - Access Marketplace',
});

const authStore = useAuthStore();
const uiStore = useUiStore();
const router = useRouter();
const route = useRoute();

const loginError = ref<string | null>(null);

const loginSchema = object({
  email: string().required('Email is required').email('Must be a valid email address'),
  password: string().required('Password is required').min(8, 'Password must be at least 8 characters'),
  remember: boolean(),
});

interface LoginFormValues {
  email: string;
  password: string;
  remember?: boolean;
}

const handleLogin = async (values: LoginFormValues, { setErrors }) => {
  loginError.value = null;
  try {
    await authStore.login({
      email: values.email,
      password: values.password,
    });

    // uiStore.showToast('Login successful! Welcome back.', 'success'); // Handled by Toaster in app.vue

    // Redirect to dashboard or intended page
    const redirectPath = route.query.redirect || '/dashboard';
    router.push(redirectPath as string);

  } catch (error: any) {
    if (error.data && error.data.errors) {
      // If backend returns field-specific errors
      const fieldErrors: Record<string, string> = {};
      for (const key in error.data.errors) {
        fieldErrors[key] = error.data.errors[key][0]; // Take the first error message for each field
      }
      setErrors(fieldErrors);
      loginError.value = error.message || "Login failed. Please check the highlighted fields.";
    } else {
      loginError.value = error.message || 'An unexpected error occurred during login.';
    }
    // uiStore.showToast(loginError.value, 'error'); // Handled by Toaster in app.vue
  }
};

onMounted(() => {
  if (route.query.sessionExpired) {
    loginError.value = "Your session has expired. Please log in again.";
    // uiStore.showToast(loginError.value, 'warning'); // Handled by Toaster in app.vue
  }
  if (route.query.registered) {
    // uiStore.showToast("Registration successful! Please log in.", "success"); // Handled by Toaster in app.vue
  }
});
</script>

<style scoped lang="scss">
.auth-page-container {
  // Background pattern or subtle animation can be added here
  // Example: using a SVG pattern for the background
  background-image: radial-gradient(circle at top left, rgba(127, 90, 240, 0.05) 0%, transparent 30%),
                    radial-gradient(circle at bottom right, rgba(44, 182, 125, 0.05) 0%, transparent 30%);
}

// Additional specific styles for form elements if needed
// .form-input-base from main.css should cover most styling
</style>
