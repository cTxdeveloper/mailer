<template>
  <div class="nexus-mascot-placeholder" :style="placeholderStyle" title="Nexus Mascot - 3D element placeholder">
    <div class="placeholder-core" :style="coreStyle">
      <PhAtom v-if="!imageUrl" :style="{ color: color, fontSize: size * 0.6 + 'px' }" weight="light" />
    </div>
    <img v-if="imageUrl" :src="imageUrl" alt="Nexus Mascot" class="w-full h-full object-contain" />
    <p v-if="debug" class="debug-text">Nexus 3D Placeholder</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { PhAtom } from 'phosphor-vue'; // Using an icon as a simple placeholder

const props = defineProps({
  size: {
    type: Number,
    default: 100, // Default size in pixels
  },
  color: {
    type: String,
    default: '#7F5AF0', // Quantum Purple
  },
  animationState: { // 'idle', 'assembling', 'guarding', 'interacting'
    type: String,
    default: 'idle',
  },
  imageUrl: { // Optional image URL to use instead of the SVG/CSS placeholder
    type: String,
    default: null, // e.g. '/nexus-static-placeholder.png'
  },
  debug: {
    type: Boolean,
    default: false,
  }
});

const placeholderStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  // border: `2px dashed ${props.color}`,
  // borderRadius: '50%', // Make it circular for a basic shape
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  position: 'relative', // For potential future animations or overlays
  // backgroundColor: 'rgba(127, 90, 240, 0.05)', // Very light purple bg
}));

const coreStyle = computed(() => ({
  width: `${props.size * 0.7}px`,
  height: `${props.size * 0.7}px`,
  borderRadius: '50%',
  backgroundColor: `rgba(127, 90, 240, ${props.animationState === 'guarding' ? 0.3 : 0.15})`,
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  transition: 'all 0.5s ease',
  animation: props.animationState === 'idle' ? 'subtlePulse 3s infinite ease-in-out' : 'none',
  boxShadow: props.animationState === 'guarding' ? `0 0 ${props.size * 0.2}px ${props.size * 0.05}px rgba(127, 90, 240, 0.7)`: `0 0 ${props.size * 0.1}px rgba(127, 90, 240, 0.3)`,
}));

// Placeholder for future Three.js integration
// onMounted(() => {
//   if (process.client && !props.imageUrl) {
//     // Initialize Three.js scene here
//     // Example: import { initNexus } from '~/three/nexusRenderer';
//     //          initNexus(containerRef.value, props);
//   }
// });

// const containerRef = ref(null); // To mount Three.js scene

</script>

<style scoped lang="scss">
.nexus-mascot-placeholder {
  // Basic styling for the placeholder
  // This could be enhanced with CSS animations based on `animationState` prop
  // For example, a pulsing glow or a simple rotation.
}

.placeholder-core {
  // Styles for the inner "core" of the placeholder
}

@keyframes subtlePulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.05);
    opacity: 1;
  }
}

.debug-text {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: #aaa;
  background-color: rgba(0,0,0,0.5);
  padding: 2px 4px;
  border-radius: 3px;
}

// Example of how animationState could be used for different looks:
// .nexus-mascot-placeholder[data-animation-state="assembling"] .placeholder-core {
//   animation: assembleEffect 1.5s ease-out;
// }
// @keyframes assembleEffect { /* ... */ }

// .nexus-mascot-placeholder[data-animation-state="guarding"] .placeholder-core {
//   box-shadow: 0 0 20px 5px var(--color-prop, #7F5AF0); /* Use CSS var for color */
// }
</style>
