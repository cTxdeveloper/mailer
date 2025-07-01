<template>
  <NuxtLink v-if="to" :to="to" :class="buttonClasses" :aria-label="ariaLabel || (typeof $slots.default === 'function' ? $slots.default()[0]?.children : 'button')">
    <slot name="prepend"></slot>
    <v-progress-circular
      v-if="loading"
      indeterminate
      :size="size === 'small' ? 16 : 20"
      :width="2"
      class="mr-2"
      :color="variant === 'solid' || variant === 'default' ? (color === 'quantum-purple' || color === 'guardian-green' ? 'white' : 'primary') : color"
    ></v-progress-circular>
    <slot></slot>
    <slot name="append"></slot>
  </NuxtLink>
  <button v-else :type="type" :class="buttonClasses" :disabled="disabled || loading" @click="$emit('click', $event)" :aria-label="ariaLabel || (typeof $slots.default === 'function' ? $slots.default()[0]?.children : 'button')">
    <slot name="prepend"></slot>
    <v-progress-circular
      v-if="loading"
      indeterminate
      :size="size === 'small' ? 16 : 20"
      :width="2"
      class="mr-2"
      :color="variant === 'solid' || variant === 'default' ? (color === 'quantum-purple' || color === 'guardian-green' ? 'white' : 'primary') : color"
    ></v-progress-circular>
    <slot></slot>
    <slot name="append"></slot>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type ButtonVariant = 'solid' | 'outline' | 'ghost' | 'text' | 'default';
type ButtonSize = 'small' | 'medium' | 'large' | 'default';
type ButtonColor = 'quantum-purple' | 'guardian-green' | 'danger-red' | 'pure-white' | 'obsidian-black' | 'default' | string; // Allow any string for custom colors

const props = defineProps({
  to: {
    type: String,
    default: null,
  },
  type: {
    type: String as () => 'button' | 'submit' | 'reset',
    default: 'button',
  },
  variant: {
    type: String as () => ButtonVariant,
    default: 'default', // 'default' will behave like 'solid' with primary color
  },
  size: {
    type: String as () => ButtonSize,
    default: 'default', // 'default' will be medium
  },
  color: {
    type: String as () => ButtonColor,
    default: 'default', // 'default' will be quantum-purple
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  block: { // Makes button full width
    type: Boolean,
    default: false,
  },
  rounded: { // For fully rounded pill shape
    type: Boolean,
    default: false,
  },
  ariaLabel: {
    type: String,
    default: '',
  }
});

defineEmits(['click']);

const baseClasses = 'inline-flex items-center justify-center font-semibold focus:outline-none transition-all duration-200 ease-in-out transform active:scale-95';

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'small':
      return 'px-3 py-1.5 text-xs';
    case 'large':
      return 'px-8 py-3 text-lg';
    case 'medium':
    case 'default':
    default:
      return 'px-5 py-2.5 text-sm';
  }
});

const colorClasses = computed(() => {
  const effectiveColor = props.color === 'default' ? 'quantum-purple' : props.color;
  const commonDisabled = 'disabled:opacity-50 disabled:cursor-not-allowed';

  switch (props.variant) {
    case 'solid':
    case 'default':
      return {
        'quantum-purple': `bg-quantum-purple text-pure-white hover:bg-purple-500 focus:ring-2 focus:ring-quantum-purple focus:ring-opacity-50 ${commonDisabled}`,
        'guardian-green': `bg-guardian-green text-pure-white hover:bg-green-500 focus:ring-2 focus:ring-guardian-green focus:ring-opacity-50 ${commonDisabled}`,
        'danger-red': `bg-danger-red text-pure-white hover:bg-red-500 focus:ring-2 focus:ring-danger-red focus:ring-opacity-50 ${commonDisabled}`,
        'pure-white': `bg-pure-white text-obsidian-black hover:bg-gray-200 focus:ring-2 focus:ring-gray-300 focus:ring-opacity-50 ${commonDisabled}`,
        'obsidian-black': `bg-obsidian-black text-pure-white hover:bg-gray-800 focus:ring-2 focus:ring-gray-700 focus:ring-opacity-50 ${commonDisabled}`,
      }[effectiveColor] || `bg-${effectiveColor}-500 text-white hover:bg-${effectiveColor}-600 focus:ring-2 focus:ring-${effectiveColor}-500 ${commonDisabled}`; // Fallback for custom string colors
    case 'outline':
      return {
        'quantum-purple': `border-2 border-quantum-purple text-quantum-purple hover:bg-quantum-purple hover:text-pure-white focus:ring-2 focus:ring-quantum-purple focus:ring-opacity-50 ${commonDisabled}`,
        'guardian-green': `border-2 border-guardian-green text-guardian-green hover:bg-guardian-green hover:text-pure-white focus:ring-2 focus:ring-guardian-green focus:ring-opacity-50 ${commonDisabled}`,
        'danger-red': `border-2 border-danger-red text-danger-red hover:bg-danger-red hover:text-pure-white focus:ring-2 focus:ring-danger-red focus:ring-opacity-50 ${commonDisabled}`,
        'pure-white': `border-2 border-pure-white text-pure-white hover:bg-pure-white hover:text-obsidian-black focus:ring-2 focus:ring-pure-white focus:ring-opacity-50 ${commonDisabled}`,
        'obsidian-black': `border-2 border-obsidian-black text-obsidian-black hover:bg-obsidian-black hover:text-pure-white focus:ring-2 focus:ring-obsidian-black focus:ring-opacity-50 ${commonDisabled}`,
      }[effectiveColor] || `border-2 border-${effectiveColor}-500 text-${effectiveColor}-500 hover:bg-${effectiveColor}-500 hover:text-white focus:ring-2 focus:ring-${effectiveColor}-500 ${commonDisabled}`;
    case 'ghost':
      return {
        'quantum-purple': `text-quantum-purple hover:bg-quantum-purple/10 focus:ring-2 focus:ring-quantum-purple/30 ${commonDisabled}`,
        'guardian-green': `text-guardian-green hover:bg-guardian-green/10 focus:ring-2 focus:ring-guardian-green/30 ${commonDisabled}`,
        'danger-red': `text-danger-red hover:bg-danger-red/10 focus:ring-2 focus:ring-danger-red/30 ${commonDisabled}`,
        'pure-white': `text-pure-white hover:bg-pure-white/10 focus:ring-2 focus:ring-pure-white/30 ${commonDisabled}`,
        'obsidian-black': `text-obsidian-black hover:bg-obsidian-black/10 focus:ring-2 focus:ring-obsidian-black/30 ${commonDisabled}`,
      }[effectiveColor] || `text-${effectiveColor}-500 hover:bg-${effectiveColor}-500/10 focus:ring-2 focus:ring-${effectiveColor}-500/30 ${commonDisabled}`;
    case 'text':
      return {
        'quantum-purple': `text-quantum-purple hover:text-purple-400 focus:ring-1 focus:ring-quantum-purple/20 ${commonDisabled} !p-1`, // Minimal padding for text buttons
        'guardian-green': `text-guardian-green hover:text-green-400 focus:ring-1 focus:ring-guardian-green/20 ${commonDisabled} !p-1`,
        'danger-red': `text-danger-red hover:text-red-400 focus:ring-1 focus:ring-danger-red/20 ${commonDisabled} !p-1`,
        'pure-white': `text-pure-white hover:text-gray-300 focus:ring-1 focus:ring-pure-white/20 ${commonDisabled} !p-1`,
        'obsidian-black': `text-obsidian-black hover:text-gray-700 focus:ring-1 focus:ring-obsidian-black/20 ${commonDisabled} !p-1`,
      }[effectiveColor] || `text-${effectiveColor}-500 hover:text-${effectiveColor}-400 focus:ring-1 focus:ring-${effectiveColor}-500/20 ${commonDisabled} !p-1`;
    default:
      return '';
  }
});

const buttonClasses = computed(() => [
  baseClasses,
  sizeClasses.value,
  colorClasses.value,
  props.block ? 'w-full' : '',
  props.rounded ? 'rounded-full' : 'rounded-lg',
  props.loading ? 'cursor-wait' : '',
  { 'opacity-75 cursor-not-allowed': props.disabled && !props.loading },
]);

</script>

<style scoped>
/* Add any specific styles that Tailwind classes can't easily cover */
/* For example, a subtle shine effect on hover for solid buttons */
.bg-quantum-purple:not(:disabled):hover, .bg-guardian-green:not(:disabled):hover {
  /* You could add a pseudo-element for shine here if desired */
}

/* Ensure loading spinner is centered if slot content is empty */
button:empty .v-progress-circular, a:empty .v-progress-circular {
  margin-right: 0;
}
</style>
