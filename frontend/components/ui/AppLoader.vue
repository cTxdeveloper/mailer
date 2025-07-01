<template>
  <div class="app-loader-wrapper" :class="{ 'fullscreen': fullscreen, 'inline': inline }">
    <div class="loader-container" :style="{ transform: `scale(${scale})` }">
      <div class="nexus-crystal">
        <div class="facet facet-1"></div>
        <div class="facet facet-2"></div>
        <div class="facet facet-3"></div>
        <div class="facet facet-4"></div>
        <div class="facet facet-5"></div>
        <div class="facet facet-6"></div>
        <div class="core-glow"></div>
      </div>
      <p v-if="message" class="loader-message text-sm text-gray-300 mt-4 font-medium">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  message: {
    type: String,
    default: 'Loading, please wait...'
  },
  fullscreen: {
    type: Boolean,
    default: false
  },
  inline: { // For smaller, inline usage
    type: Boolean,
    default: false
  },
  scale: { // Allows scaling the loader
    type: Number,
    default: 1
  }
});
</script>

<style scoped lang="scss">
.app-loader-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;

  &.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(16, 16, 20, 0.85); /* Obsidian Black with opacity */
    z-index: 9999;
    backdrop-filter: blur(8px);
  }

  &.inline {
    padding: 1rem 0; // Some padding for inline usage
    // background-color: transparent !important; // Ensure no background for inline
  }
}

.loader-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

$crystal-size: 60px;
$animation-duration: 2.5s;
$purple-glow: #7F5AF0;
$white-glow: #FFFFFF;

.nexus-crystal {
  width: $crystal-size;
  height: $crystal-size;
  position: relative;
  animation: rotateCrystal $animation-duration infinite linear, pulseCrystal $animation-duration infinite ease-in-out;
  transform-style: preserve-3d; // Important for 3D effect of facets

  .facet {
    position: absolute;
    width: 100%;
    height: 100%;
    border: 1px solid rgba($purple-glow, 0.5);
    background: linear-gradient(45deg, rgba($purple-glow, 0.1), rgba($white-glow, 0.1));
    opacity: 0.7;
    box-shadow: inset 0 0 10px rgba($purple-glow, 0.3);
  }

  // Define positions and rotations for a more 3D-like crystal structure
  // These are simplified; a true 3D crystal would be more complex
  .facet-1 { transform: rotateY(0deg) translateZ(calc($crystal-size / 2)); }
  .facet-2 { transform: rotateY(60deg) translateZ(calc($crystal-size / 2)); }
  .facet-3 { transform: rotateY(120deg) translateZ(calc($crystal-size / 2)); }
  .facet-4 { transform: rotateY(180deg) translateZ(calc($crystal-size / 2)); }
  .facet-5 { transform: rotateY(240deg) translateZ(calc($crystal-size / 2)); }
  .facet-6 { transform: rotateY(300deg) translateZ(calc($crystal-size / 2)); }
  // Could add top/bottom facets as well with rotateX

  .core-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    width: calc($crystal-size / 2);
    height: calc($crystal-size / 2);
    background: radial-gradient(ellipse at center, $white-glow 0%, rgba($purple-glow, 0.5) 70%, rgba($purple-glow, 0) 100%);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    animation: pulseCore $animation-duration * 0.6 infinite ease-in-out alternate;
    filter: blur(3px);
  }
}

@keyframes rotateCrystal {
  from { transform: rotateY(0deg) rotateX(10deg); }
  to { transform: rotateY(360deg) rotateX(10deg); }
}

@keyframes pulseCrystal {
  0%, 100% { filter: drop-shadow(0 0 5px $purple-glow); opacity: 0.8; }
  50% { filter: drop-shadow(0 0 15px $white-glow) drop-shadow(0 0 25px $purple-glow); opacity: 1; }
}

@keyframes pulseCore {
  from { transform: translate(-50%, -50%) scale(0.8); opacity: 0.7; }
  to { transform: translate(-50%, -50%) scale(1.1); opacity: 1; }
}

.loader-message {
  animation: fadeInMessage 1s ease-in-out forwards;
  animation-delay: 0.5s; // Delay message appearance slightly
  opacity: 0; // Start hidden
}

@keyframes fadeInMessage {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

// Smaller version for inline usage
.app-loader-wrapper.inline .nexus-crystal {
  $crystal-size-inline: 30px;
  width: $crystal-size-inline;
  height: $crystal-size-inline;

  .facet-1 { transform: rotateY(0deg) translateZ(calc($crystal-size-inline / 2)); }
  .facet-2 { transform: rotateY(60deg) translateZ(calc($crystal-size-inline / 2)); }
  .facet-3 { transform: rotateY(120deg) translateZ(calc($crystal-size-inline / 2)); }
  .facet-4 { transform: rotateY(180deg) translateZ(calc($crystal-size-inline / 2)); }
  .facet-5 { transform: rotateY(240deg) translateZ(calc($crystal-size-inline / 2)); }
  .facet-6 { transform: rotateY(300deg) translateZ(calc($crystal-size-inline / 2)); }

  .core-glow {
    width: calc($crystal-size-inline / 2);
    height: calc($crystal-size-inline / 2);
  }
}
.app-loader-wrapper.inline .loader-message {
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

</style>
