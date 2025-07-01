<template>
  <div class="form-textarea-container relative mb-5" :class="{ 'has-error': !!errorMessage, 'is-filled': isFilled }">
    <label v-if="label" :for="textareaId" class="block text-sm font-medium text-gray-300 mb-1.5 transition-all duration-200 ease-in-out" :class="{'label-floating': isFocused || isFilled, 'text-quantum-purple': isFocused}">
      {{ label }}
      <span v-if="required" class="text-danger-red">*</span>
    </label>
    <div class="relative">
      <textarea
        :id="textareaId"
        :name="name"
        :value="inputValue"
        @input="handleChange"
        @blur="handleBlur"
        @focus="handleFocus"
        :placeholder="placeholderToShow"
        :disabled="disabled"
        :required="required"
        :rows="rows"
        v-bind="$attrs"
        class="form-input-base w-full py-2.5 rounded-md bg-obsidian-black/30 border text-pure-white placeholder-gray-500 focus:ring-quantum-purple focus:border-quantum-purple transition-all duration-200 ease-in-out resize-vertical min-h-[80px]"
        :class="[
          { 'border-danger-red focus:border-danger-red focus:ring-danger-red': !!errorMessage },
          { 'border-gray-600 hover:border-gray-500': !errorMessage && !isFocused },
          { 'border-quantum-purple shadow-glow-purple-sm': isFocused && !errorMessage },
        ]"
      ></textarea>
      <div class="nexus-shard" :class="{ 'active': isFocused }"></div>
      <div v-if="showCharCount" class="char-counter text-xs text-gray-400 absolute bottom-2 right-2 bg-obsidian-black/50 px-1 rounded">
        {{ charCount }}/{{ maxLength }}
      </div>
    </div>
    <VeeErrorMessage :name="name" as="p" class="mt-1.5 text-xs text-danger-red animate-fade-in" />
    <p v-if="hint && !errorMessage" class="mt-1.5 text-xs text-gray-400">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { toRef, ref, computed, getCurrentInstance } from 'vue';
import { useField } from 'vee-validate';

interface ComponentInstance {
  uid: number;
}

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  name: {
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
  rows: {
    type: Number,
    default: 3,
  },
  rules: {
    type: [String, Object, Function],
    default: undefined,
  },
  floatingLabel: {
    type: Boolean,
    default: true,
  },
  maxLength: {
    type: Number,
    default: null,
  },
  showCharCount: {
    type: Boolean,
    default: false,
  }
});

const emit = defineEmits(['update:modelValue']);

const textareaId = ref(`form-textarea-${getCurrentInstance()?.uid || Math.random().toString(36).substring(7)}`);
const isFocused = ref(false);

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

const charCount = computed(() => inputValue.value?.length || 0);

const handleFocus = () => {
  isFocused.value = true;
};

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false;
  veeHandleBlur(event);
};

const handleChange = (event: Event) => {
  const target = event.target as HTMLTextAreaElement;
  let value = target.value;
  if (props.maxLength && value.length > props.maxLength) {
    value = value.substring(0, props.maxLength);
    // Update the input field visually if it was truncated
    target.value = value;
  }
  veeHandleChange(value);
  emit('update:modelValue', value);
};

</script>

<style scoped lang="scss">
.form-input-base { /* Shared with FormInput, can be in main.css */
  appearance: none;
}

/* Floating label styles - can be shared with FormInput */
.label-floating {
  transform: translateY(-110%) translateX(-2px) scale(0.85);
  @apply text-xs;
  position: absolute;
  top: 0.625rem;
  left: 0.75rem;
  background-color: var(--v-theme-background);
  padding: 0 0.25rem;
  pointer-events: none;
}

/* Nexus Shard - can be shared with FormInput */
.nexus-shard {
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background-color: var(--v-color-quantum-purple);
  transition: width 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  border-radius: 1px;
  opacity: 0;
}

.nexus-shard.active {
  width: 40%;
  opacity: 1;
}

/* Error message animation - can be shared */
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.char-counter {
  pointer-events: none; /* So it doesn't interfere with textarea interaction */
}

textarea.form-input-base {
  line-height: 1.6; /* Improve readability for multiline text */
}
</style>
