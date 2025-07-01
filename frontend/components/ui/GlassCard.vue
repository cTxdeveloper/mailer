<template>
  <div :class="['glass-card p-4 md:p-6 shadow-xl transition-all duration-300 ease-in-out', cardClasses, { 'noise-bg': applyNoise }]" @mousemove="handleMouseMove" @mouseleave="handleMouseLeave" ref="cardRef">
    <div class="card-content-wrapper" :style="contentStyle">
      <div v-if="hasHeaderSlot || title" class="card-header mb-4 pb-3 border-b border-white/10 flex justify-between items-center">
        <slot name="header">
          <h3 v-if="title" class="text-lg md:text-xl font-semibold text-pure-white font-display">{{ title }}</h3>
        </slot>
        <slot name="header-actions"></slot>
      </div>
      <slot></slot>
      <div v-if="hasFooterSlot" class="card-footer mt-4 pt-3 border-t border-white/10">
        <slot name="footer"></slot>
      </div>
    </div>
    <div v-if="interactiveGlow" class="glow-effect" :style="glowStyle"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, useSlots, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  title: {
    type: String,
    default: '',
  },
  padding: {
    type: String, // e.g., 'p-0', 'p-8'
    default: '', // Handled by base p-4 md:p-6, but can be overridden
  },
  hoverEffect: { // 'none', 'lift', 'glow-border'
    type: String,
    default: 'lift', // Default hover effect
  },
  interactiveGlow: { // Adds a mouse-following glow effect inside the card
    type: Boolean,
    default: false,
  },
  tiltEffect: { // Adds a 3D tilt effect on hover
    type: Boolean,
    default: false,
  },
  borderColor: { // e.g. 'border-quantum-purple/50'
    type: String,
    default: 'border-white/10',
  },
  backgroundColor: { // e.g. 'bg-obsidian-black/70'
    type: String,
    default: 'bg-glass-bg', // Uses the default glass background from main.css
  },
  blurAmount: { // e.g. 'backdrop-blur-md'
    type: String,
    default: 'backdrop-blur-lg',
  },
  borderRadius: { // e.g. 'rounded-lg', 'rounded-2xl'
    type: String,
    default: 'rounded-xl',
  },
  applyNoise: { // Whether to apply the subtle noise background
    type: Boolean,
    default: true,
  }
});

const slots = useSlots();
const hasHeaderSlot = computed(() => !!slots.header || !!props.title);
const hasFooterSlot = computed(() => !!slots.footer);

const cardRef = ref<HTMLElement | null>(null);
const glowPosition = ref({ x: 0, y: 0, opacity: 0 });
const tiltRotation = ref({ x: 0, y: 0 });

const cardClasses = computed(() => [
  props.padding || '',
  props.borderColor,
  props.backgroundColor,
  props.blurAmount,
  props.borderRadius,
  {
    'hover:transform hover:-translate-y-1 hover:shadow-2xl': props.hoverEffect === 'lift',
    'hover:shadow-glow-purple-md': props.hoverEffect === 'glow-border', // Needs corresponding shadow in tailwind.config
    'transform-style-3d': props.tiltEffect,
  }
]);

const contentStyle = computed(() => {
  if (props.tiltEffect) {
    return {
      transform: `rotateX(${tiltRotation.value.x}deg) rotateY(${tiltRotation.value.y}deg) translateZ(20px)`, // translateZ for content pop
      transition: 'transform 0.1s linear'
    };
  }
  return {};
});

const glowStyle = computed(() => ({
  left: `${glowPosition.value.x}px`,
  top: `${glowPosition.value.y}px`,
  opacity: glowPosition.value.opacity,
  background: `radial-gradient(circle at center, rgba(127, 90, 240, 0.2) 0%, rgba(127, 90, 240, 0) 70%)`,
}));


const handleMouseMove = (event: MouseEvent) => {
  if (!cardRef.value) return;
  const rect = cardRef.value.getBoundingClientRect();

  if (props.interactiveGlow) {
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    glowPosition.value = { x, y, opacity: 1 };
  }

  if (props.tiltEffect) {
    const x = event.clientX - rect.left - rect.width / 2;
    const y = event.clientY - rect.top - rect.height / 2;
    const rotateX = -(y / rect.height) * 10; // Max rotation 5 degrees
    const rotateY = (x / rect.width) * 10;  // Max rotation 5 degrees
    tiltRotation.value = { x: rotateX, y: rotateY };
  }
};

const handleMouseLeave = () => {
  if (props.interactiveGlow) {
    glowPosition.value.opacity = 0;
  }
  if (props.tiltEffect) {
    tiltRotation.value = { x: 0, y: 0 };
  }
};

onMounted(() => {
  // Any setup if needed
});

onUnmounted(() => {
  // Cleanup if needed
});

</script>

<style scoped lang="scss">
.glass-card {
  position: relative; /* Needed for glow effect positioning */
  // The base glass effect (bg-glass-bg, backdrop-blur-lg, border, rounded-xl, shadow-lg)
  // is applied via Tailwind directives in main.css or directly here.
  // We are using props to make it more configurable.
  // Default values are set in main.css via .glass-effect
  // This component allows overriding them.
  overflow: hidden; /* Important for glow effect not to spill out too much */
}

.card-content-wrapper {
  position: relative;
  z-index: 1; /* Content above the glow */
}

.transform-style-3d {
  transform-style: preserve-3d;
  transition: transform 0.1s linear; /* Smooth return for tilt */
}

.glow-effect {
  position: absolute;
  width: 300px; /* Size of the glow */
  height: 300px;
  border-radius: 50%;
  pointer-events: none; /* So it doesn't interfere with mouse events on the card */
  transition: opacity 0.3s ease-out, transform 0.3s ease-out;
  transform: translate(-50%, -50%); /* Center the glow on the mouse position */
  z-index: 0; /* Behind the content */
  filter: blur(30px); /* Soften the glow */
}

/* Optional: add a subtle pattern or noise to the background if not using .noise-bg prop */
/* .glass-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: url('/path-to-noise-texture.png'); // Or SVG noise
  opacity: 0.03;
  pointer-events: none;
  z-index: 0;
} */
</style>
