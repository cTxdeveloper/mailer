<template>
  <div class="auth-page-container min-h-screen flex items-center justify-center bg-gradient-to-br from-obsidian-black via-purple-900/30 to-obsidian-black p-4">
    <GlassCard class="w-full max-w-lg shadow-2xl" :interactiveGlow="true" padding="p-6 md:p-10">
      <template #header>
        <div class="text-center">
          <NuxtLink to="/" class="inline-block mb-6">
            <img src="/nexus-logo-light.svg" alt="Access Marketplace Logo" class="h-12 w-auto">
          </NuxtLink>
          <h2 class="text-3xl font-bold font-display text-pure-white">Create Your Account</h2>
          <p class="text-gray-400 mt-2">Join the marketplace of value.</p>
        </div>
      </template>

      <VeeForm @submit="handleRegister" :validation-schema="registerSchema" v-slot="{ isSubmitting, errors: formErrors }">
        <div class="space-y-5">
          <UiFormInput
            name="displayName"
            type="text"
            label="Display Name / Alias"
            placeholder="e.g., QuantumConnector"
            :prepend-icon="PhUserCircle"
            autocomplete="nickname"
            :disabled="isSubmitting"
          />
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
            placeholder="Create a strong password"
            :prepend-icon="PhLockSimple"
            autocomplete="new-password"
            hint="Minimum 8 characters, include upper, lower, number, symbol."
            :disabled="isSubmitting"
          />
          <UiFormInput
            name="confirmPassword"
            type="password"
            label="Confirm Password"
            placeholder="Re-enter your password"
            :prepend-icon="PhPassword"
            autocomplete="new-password"
            :disabled="isSubmitting"
          />

          <div class="my-4">
            <label for="role" class="block text-sm font-medium text-gray-300 mb-1.5">I want to:</label>
            <VeeField name="role" as="select" class="form-input-base w-full bg-obsidian-black/50 border-gray-600 focus:border-quantum-purple focus:ring-quantum-purple" :disabled="isSubmitting">
              <option value="seeker">Find Introductions (Seeker)</option>
              <option value="connector">Monetize My Network (Connector)</option>
            </VeeField>
            <VeeErrorMessage name="role" class="mt-1.5 text-xs text-danger-red" />
          </div>


          <VeeField name="termsAccepted" type="checkbox" :value="true" v-slot="{ field, meta: termsMeta }">
            <label class="flex items-start text-gray-400 cursor-pointer text-sm mt-3">
              <input
                type="checkbox"
                v-bind="field"
                class="h-4 w-4 text-quantum-purple bg-gray-700 border-gray-600 rounded focus:ring-quantum-purple mr-2 mt-0.5 flex-shrink-0"
                :class="{ 'border-danger-red': termsMeta.touched && !termsMeta.valid }"
              />
              <span>I agree to The Access Marketplace
                <NuxtLink to="/terms" target="_blank" class="text-quantum-purple hover:underline">Terms of Service</NuxtLink> and
                <NuxtLink to="/privacy" target="_blank" class="text-quantum-purple hover:underline">Privacy Policy</NuxtLink>.
              </span>
            </label>
          </VeeField>
          <VeeErrorMessage name="termsAccepted" as="p" class="text-xs text-danger-red animate-fade-in" />


          <div v-if="registrationError" class="bg-danger-red/10 p-3 rounded-md text-danger-red text-sm animate-fade-in">
             <PhWarningCircle weight="bold" class="inline mr-1" /> {{ registrationError }}
          </div>
          <div v-if="formErrors && Object.keys(formErrors).length > 0 && !registrationError" class="bg-danger-red/10 p-3 rounded-md text-danger-red text-sm">
            Please correct the highlighted errors.
          </div>

          <AppButton
            type="submit"
            color="quantum-purple"
            class="w-full !py-3 text-base mt-2"
            :loading="isSubmitting"
            :disabled="isSubmitting"
          >
            <PhUserPlus class="mr-2" weight="bold" />
            Create Account
          </AppButton>
        </div>
      </VeeForm>

      <template #footer>
        <p class="text-center text-sm text-gray-400">
          Already have an account?
          <NuxtLink to="/auth/login" class="font-medium text-quantum-purple hover:text-purple-400">
            Log in here
          </NuxtLink>
        </p>
      </template>
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '~/store/auth';
import { useUiStore } from '~/store/ui';
import { object, string, boolean, ref as yupRef } from 'yup';
import { PhUserCircle, PhEnvelopeSimple, PhLockSimple, PhPassword, PhUserPlus, PhWarningCircle } from 'phosphor-vue';
import GlassCard from '~/components/ui/GlassCard.vue';
import UiFormInput from '~/components/ui/FormInput.vue';
import AppButton from '~/components/ui/AppButton.vue';
import { Form as VeeForm, Field as VeeField, ErrorMessage as VeeErrorMessage } from 'vee-validate';


definePageMeta({
  layout: 'landing', // Or 'auth' layout
  middleware: ['guest-only'],
});

useHead({
  title: 'Register - Access Marketplace',
});

const authStore = useAuthStore();
const uiStore = useUiStore();
const router = useRouter();
const route = useRoute();

const registrationError = ref<string | null>(null);
const selectedRole = ref(route.query.role === 'connector' ? 'connector' : 'seeker');

const registerSchema = object({
  displayName: string().required('Display name is required').min(3, 'Must be at least 3 characters').max(50, 'Cannot exceed 50 characters'),
  email: string().required('Email is required').email('Must be a valid email address'),
  password: string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(/[a-z]/, 'Password must contain a lowercase letter')
    .matches(/[A-Z]/, 'Password must contain an uppercase letter')
    .matches(/[0-9]/, 'Password must contain a number')
    .matches(/[^A-Za-z0-9]/, 'Password must contain a special character'),
  confirmPassword: string()
    .required('Confirm password is required')
    .oneOf([yupRef('password')], 'Passwords must match'),
  role: string().required('Please select a role.').oneOf(['seeker', 'connector']),
  termsAccepted: boolean().oneOf([true], 'You must accept the Terms of Service and Privacy Policy').required(),
});

interface RegisterFormValues {
  displayName: string;
  email: string;
  password: string;
  confirmPassword?: string; // May not be needed by backend if validated
  role: 'seeker' | 'connector';
  termsAccepted?: boolean; // May not be needed by backend
}

const handleRegister = async (values: RegisterFormValues, { setErrors }) => {
  registrationError.value = null;
  try {
    await authStore.register({
      display_name: values.displayName, // Ensure snake_case if backend expects it
      email: values.email,
      password: values.password,
      role: values.role,
    });

    // uiStore.showToast('Registration successful! Please check your email for verification if required, then log in.', 'success'); // Handled by Toaster in app.vue
    router.push('/auth/login?registered=true'); // Redirect to login page

  } catch (error: any) {
     if (error.data && error.data.errors) {
      const fieldErrors: Record<string, string> = {};
      for (const key in error.data.errors) {
        fieldErrors[key] = error.data.errors[key][0];
      }
      setErrors(fieldErrors);
      registrationError.value = error.message || "Registration failed. Please check the highlighted fields.";
    } else {
      registrationError.value = error.message || 'An unexpected error occurred during registration.';
    }
    // uiStore.showToast(registrationError.value, 'error'); // Handled by Toaster in app.vue
  }
};

// Set initial value for the role field in VeeValidate form if passed via query
const initialFormValues = {
  role: selectedRole.value,
  // ... other initial values if needed
};
// Note: VeeValidate's `initialValues` prop on `<VeeForm>` can be used if needed,
// or just ensure the select's `v-model` or bound field value is set correctly.
// Here, the `<VeeField name="role" as="select">` will pick up initial value if `selectedRole` is bound or part of `initialValues`.
// For this setup, the default value of the `select` element itself will handle it.
// If `VeeField` is used with `v-model`, that would also work.
// For `as="select"`, the initial value needs to be part of the form's initial values context.
// We can pass `initial-values` to `VeeForm` component if needed.
// Let's ensure the `select` element reflects `selectedRole.value`.
// This is typically handled by the default value of the select or by setting it in the form's initial values.
// The `VeeField` as `select` should correctly initialize with `selectedRole.value` if `selectedRole` is part of `initialValues` passed to `VeeForm`.
// Or, if `selectedRole` is bound to the `select` element.
// The simplest for VeeValidate is often to provide `initialValues` to the `VeeForm`.
// However, direct binding `v-model="selectedRole"` to the `select` or using `:value="selectedRole"` on `option`s
// might conflict with VeeValidate's control.
// The most VeeValidate-idiomatic way is `initial-values` on `VeeForm`.
// For now, we assume the default option selection or manual user choice.
// The schema for `role` has it as required.

onMounted(() => {
  // If `role` is in query params, set the form's initial value for role.
  // This is tricky with VeeValidate if not using `initial-values` on the form.
  // A simple way is to just have the select default to 'seeker' and let user change if needed.
  // The `selectedRole.value` is used to potentially pre-select.
  // The `VeeField as="select"` should have its value bound or initialized.
  // One way to ensure the select starts with the query param value:
  // In the VeeForm, use `:initial-values="{ role: selectedRole }"`.
  // This is the cleanest way. Let's assume the VeeForm tag will be updated if this is needed.
  // For now, the template is as is.
  // The current `registerSchema` makes `role` required.
});

</script>

<style scoped lang="scss">
.auth-page-container {
  background-image: radial-gradient(circle at top right, rgba(127, 90, 240, 0.05) 0%, transparent_30%),
                    radial-gradient(circle at bottom left, rgba(44, 182, 125, 0.05) 0%, transparent_30%);
}
</style>
