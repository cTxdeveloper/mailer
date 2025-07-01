<template>
  <div class="form-input-container relative mb-5" :class="{ 'has-error': !!errorMessage, 'is-filled': isFilled }">
    <label v-if="label" :for="inputId" class="block text-sm font-medium text-gray-300 mb-1.5 transition-all duration-200 ease-in-out" :class="{'label-floating': isFocused || isFilled, 'text-quantum-purple': isFocused}">
      {{ label }}
      <span v-if="required" class="text-danger-red">*</span>
    </label>
    <div class="relative">
      <div v-if="prependIcon" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-10">
        <component :is="prependIcon" class="h-5 w-5 text-gray-400" :class="{'!text-quantum-purple': isFocused}" aria-hidden="true" />
      </div>
      <input
        :id="inputId"
        :type="type"
        :name="name"
        :value="inputValue"
        @input="handleChange"
        @blur="handleBlur"
        @focus="handleFocus"
        :placeholder="placeholderToShow"
        :disabled="disabled"
        :required="required"
        :autocomplete="autocomplete"
        v-bind="$attrs"
        class="form-input-base w-full py-2.5 rounded-md bg-obsidian-black/30 border text-pure-white placeholder-gray-500 focus:ring-quantum-purple focus:border-quantum-purple transition-all duration-200 ease-in-out"
        :class="[
          { 'border-danger-red focus:border-danger-red focus:ring-danger-red': !!errorMessage },
          { 'border-gray-600 hover:border-gray-500': !errorMessage && !isFocused },
          { 'border-quantum-purple shadow-glow-purple-sm': isFocused && !errorMessage },
          { 'pl-10': !!prependIcon },
          { 'pr-10': !!appendIcon || type === 'password' }
        ]"
      />
      <div v-if="appendIcon || type === 'password'" class="absolute inset-y-0 right-0 pr-3 flex items-center z-10">
        <button v-if="type === 'password'" type="button" @click="togglePasswordVisibility" class="text-gray-400 hover:text-quantum-purple focus:outline-none">
          <PhEyeSlash v-if="!isPasswordVisible" class="h-5 w-5" />
          <PhEye v-else class="h-5 w-5" />
        </button>
        <component v-else-if="appendIcon" :is="appendIcon" class="h-5 w-5 text-gray-400" aria-hidden="true" />
      </div>
       <div class="nexus-shard" :class="{ 'active': isFocused }"></div>
    </div>
    <VeeErrorMessage :name="name" as="p" class="mt-1.5 text-xs text-danger-red animate-fade-in" />
    <p v-if="hint && !errorMessage" class="mt-1.5 text-xs text-gray-400">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { toRef, ref, computed, getCurrentInstance } from 'vue';
import { useField } from 'vee-validate';
import { PhEye, PhEyeSlash } from 'phosphor-vue';

// Define component instance type for unique ID generation
interface ComponentInstance {
  uid: number;
}

const props = defineProps({
  type: {
    type: String,
    default: 'text',
  },
  modelValue: { // Used if not using vee-validate's name prop for binding
    type: [String, Number],
    default: '',
  },
  name: { // For vee-validate
    type: String,
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  hint: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  prependIcon: { // Pass the component itself, e.g., PhUser
    type: Object,
    default: null,
  },
  appendIcon: { // Pass the component itself
    type: Object,
    default: null,
  },
  autocomplete: {
    type: String,
    default: 'off',
  },
  rules: { // Vee-validate rules
    type: [String, Object, Function],
    default: undefined,
  },
  floatingLabel: { // Whether to use floating label effect
    type: Boolean,
    default: true,
  }
});

const emit = defineEmits(['update:modelValue']);

const inputId = ref(`form-input-${getCurrentInstance()?.uid || Math.random().toString(36).substring(7)}`);
const isFocused = ref(false);
const isPasswordVisible = ref(false);

// VeeValidate integration
const nameRef = toRef(props, 'name');
const { value: inputValue, errorMessage, handleBlur: veeHandleBlur, handleChange: veeHandleChange, meta } = useField(
  nameRef,
  props.rules,
  {
    initialValue: props.modelValue,
    label: props.label || props.name,
  }
);

const isFilled = computed(() => !!inputValue.value);
const placeholderToShow = computed(() => (props.floatingLabel && props.label && (isFocused.value || isFilled.value)) ? '' : props.placeholder);

const currentType = computed(() => {
  if (props.type === 'password') {
    return isPasswordVisible.value ? 'text' : 'password';
  }
  return props.type;
});

const handleFocus = () => {
  isFocused.value = true;
};

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false;
  veeHandleBlur(event); // Call VeeValidate's blur handler
};

const handleChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  veeHandleChange(target.value); // Call VeeValidate's change handler
  emit('update:modelValue', target.value); // For standalone v-model usage
};

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value;
};

</script>

<style scoped lang="scss">
.form-input-base {
  appearance: none; /* Remove default styling in some browsers */
}

/* Floating label styles */
.label-floating {
  transform: translateY(-110%) translateX(-2px) scale(0.85);
  @apply text-xs; /* Adjust font size for floating label */
  /* Position it above the input border */
  position: absolute;
  top: 0.625rem; /* Half of py-2.5 */
  left: 0.75rem; /* Corresponds to px-3 roughly */
  background-color: var(--v-theme-background); /* Match input container background for clean overlap */
  padding: 0 0.25rem;
  pointer-events: none; /* Allow clicks to pass through to input */
}

.form-input-container.is-filled .label-floating,
.form-input-container:focus-within .label-floating {
   /* Styles already applied by :class bindings, this is a fallback or can be more specific */
}

/* Nexus Shard - tiny decorative element for focus */
.nexus-shard {
  position: absolute;
  bottom: -1px; /* Align with the bottom border */
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background-color: var(--v-color-quantum-purple);
  transition: width 0.3s cubic-bezier(0.22, 1, 0.36, 1); /* Smooth expansion */
  border-radius: 1px;
  opacity: 0;
}

.nexus-shard.active {
  width: 40%; /* Expand to a certain percentage of input width */
  opacity: 1;
}

/* Error message animation */
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Adjust label position when there's a prepend icon */
.form-input-container .label-floating {
  &.label-with-prepend { // You might need to add this class dynamically if a prepend icon exists
    left: 2.5rem; /* Adjust based on icon width and padding */
  }
}
</style>
