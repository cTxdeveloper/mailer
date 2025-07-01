<template>
  <div class="app-switch-container flex items-center" :class="{ 'opacity-50 cursor-not-allowed': disabled }">
    <label v-if="labelLeft" :for="switchId" class="mr-3 text-sm font-medium text-gray-300 cursor-pointer select-none">
      {{ labelLeft }}
    </label>
    <button
      :id="switchId"
      type="button"
      role="switch"
      :aria-checked="modelValue"
      :aria-readonly="disabled"
      :disabled="disabled"
      @click="toggleSwitch"
      class="relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-obsidian-black focus:ring-quantum-purple"
      :class="modelValue ? 'bg-quantum-purple' : 'bg-gray-600'"
    >
      <span class="sr-only">Use setting</span>
      <span
        aria-hidden="true"
        class="pointer-events-none inline-block h-5 w-5 rounded-full bg-pure-white shadow transform ring-0 transition ease-in-out duration-200"
        :class="modelValue ? 'translate-x-5' : 'translate-x-0'"
      >
        <span
          class="absolute inset-0 h-full w-full flex items-center justify-center transition-opacity duration-200 ease-in-out"
          :class="modelValue ? 'opacity-0 ease-out duration-100' : 'opacity-100 ease-in duration-200'"
        >
          <!-- Optional: Icon for OFF state -->
          <!-- <PhX v-if="offIcon" :is="offIcon" class="h-3 w-3 text-gray-500" /> -->
        </span>
        <span
          class="absolute inset-0 h-full w-full flex items-center justify-center transition-opacity duration-200 ease-in-out"
          :class="modelValue ? 'opacity-100 ease-in duration-200' : 'opacity-0 ease-out duration-100'"
        >
          <!-- Optional: Icon for ON state -->
          <!-- <PhCheck v-if="onIcon" :is="onIcon" class="h-3 w-3 text-quantum-purple" /> -->
        </span>
      </span>
    </button>
    <label v-if="labelRight" :for="switchId" class="ml-3 text-sm font-medium text-gray-300 cursor-pointer select-none">
      {{ labelRight }}
    </label>
  </div>
</template>

<script setup lang="ts">
import { ref, getCurrentInstance } from 'vue';
// import { PhCheck, PhX } from 'phosphor-vue'; // Example icons

interface ComponentInstance {
  uid: number;
}

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  labelLeft: {
    type: String,
    default: '',
  },
  labelRight: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  // onIcon: { type: Object, default: null }, // Pass icon component
  // offIcon: { type: Object, default: null }, // Pass icon component
});

const emit = defineEmits(['update:modelValue']);

const switchId = ref(`app-switch-${getCurrentInstance()?.uid || Math.random().toString(36).substring(7)}`);

const toggleSwitch = () => {
  if (!props.disabled) {
    emit('update:modelValue', !props.modelValue);
  }
};
</script>

<style scoped lang="scss">
// Additional styling can be added if Tailwind classes are not sufficient.
// For example, more complex animations on the knob or background.

// The knob's inner icons can be styled here if needed.
// .h-3.w-3 { /* ... */ }
</style>
