<template>
  <div class="manifesto-page bg-obsidian-black text-pure-white min-h-screen py-10 md:py-16">
    <div class="container mx-auto px-4 md:px-8">
      <header class="text-center mb-12 md:mb-16 animate-fade-in-up">
        <ClientOnly>
          <NexusMascot :size="120" animationState="idle" class="mx-auto mb-6 text-quantum-purple" />
        </ClientOnly>
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold font-display text-pure-white mb-4">
          The Access <span class="text-quantum-purple">Manifesto</span>
        </h1>
        <p class="text-lg md:text-xl text-gray-300 max-w-3xl mx-auto">
          Confidence Through Craftsmanship: Our Pledge to a Network of Value.
        </p>
      </header>

      <section class="manifesto-content space-y-12 md:space-y-16">
        <ManifestoPoint
          v-for="(point, index) in manifestoPoints"
          :key="index"
          :icon="point.icon"
          :title="point.title"
          :description="point.description"
          :animation-delay="`${index * 150}ms`"
        />
      </section>

      <section class="mt-16 md:mt-24 text-center animate-fade-in-up animation-delay-1000">
        <h2 class="text-3xl md:text-4xl font-bold text-pure-white mb-6 font-display">
          Join the <span class="text-guardian-green">Movement</span>
        </h2>
        <p class="text-gray-300 text-lg md:text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
          The Access Marketplace is more than a platform; it's a community dedicated to fostering genuine, high-value professional relationships. We invite you to be part of this new era of networking.
        </p>
        <AppButton to="/auth/register" size="large" color="quantum-purple" class="animate-pulse-glow-once">
          Become a Member <PhUsers class="ml-2" weight="bold" />
        </AppButton>
      </section>

      <section class="our-promise mt-16 md:mt-24 py-12 md:py-16 bg-gray-900/50 rounded-xl glass-effect">
        <div class="container mx-auto px-6 md:px-8 text-center">
          <h2 class="text-2xl md:text-3xl font-bold text-pure-white mb-4 font-display">Our Promise to You</h2>
           <PhSealCheck size="48" class="text-guardian-green mx-auto mb-4" weight="duotone" />
          <p class="text-gray-300 md:text-lg max-w-3xl mx-auto leading-relaxed">
            We are committed to building a platform that is secure, transparent, and relentlessly focused on user success. Your trust is our highest priority, and every feature, every interaction is designed with that in mind. We believe in the power of connection, and we're here to help you forge the ones that truly matter.
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PhUsers, PhHandshake, PhShieldCheck, PhSparkle, PhLock, PhEye, PhHeart, PhSealCheck, PhAtom as NexusIcon } from 'phosphor-vue';
import AppButton from '~/components/ui/AppButton.vue';
import NexusMascot from '~/components/NexusMascot.vue'; // Placeholder for Nexus visual

// Define a local component for Manifesto Points for cleaner structure
const ManifestoPoint = defineComponent({
  props: {
    icon: Object, // Phosphor icon component
    title: String,
    description: String,
    animationDelay: String,
  },
  template: `
    <div class="flex flex-col md:flex-row items-start space-y-4 md:space-y-0 md:space-x-8 p-6 glass-effect rounded-lg animate-fade-in-up" :style="{ animationDelay: animationDelay }">
      <div class="flex-shrink-0">
        <component :is="icon" size="48" class="text-quantum-purple" weight="duotone" />
      </div>
      <div>
        <h3 class="text-2xl font-semibold text-pure-white mb-2 font-display">{{ title }}</h3>
        <p class="text-gray-300 leading-relaxed text-base md:text-lg">{{ description }}</p>
      </div>
    </div>
  `
});


definePageMeta({
  layout: 'default', // Or 'landing' if you prefer that styling for static pages
});

useHead({
  title: 'Manifesto - The Access Marketplace',
  meta: [
    { name: 'description', content: 'Our principles and commitment to building a trustworthy and valuable professional networking platform.' },
    { property: 'og:title', content: 'Manifesto - The Access Marketplace' },
    { property: 'og:description', content: 'Discover the core values that drive The Access Marketplace.' },
  ],
});

const manifestoPoints = ref([
  {
    icon: PhHandshake,
    title: 'Value Over Volume',
    description: "We believe that one meaningful connection is worth more than a thousand superficial ones. Our platform is designed to facilitate introductions that lead to tangible outcomes, not just endless scrolling through profiles."
  },
  {
    icon: PhShieldCheck,
    title: 'Trust as a Cornerstone',
    description: "Every transaction, every interaction on The Access Marketplace is built upon a foundation of trust. Secure escrow, verified profiles (future goal), and transparent processes ensure peace of mind for all members."
  },
  {
    icon: PhSparkle,
    title: 'Empowerment Through Connection',
    description: "We empower individuals to leverage their professional networks in new and meaningful ways. Whether you're seeking a critical introduction or offering your connections, our platform provides the tools to unlock value."
  },
  {
    icon: PhLock,
    title: 'Privacy and Security First',
    description: "Your data and interactions are treated with the utmost respect and security. We are committed to robust privacy practices and a secure environment for all professional dealings."
  },
  {
    icon: PhEye,
    title: 'Transparency in All Things',
    description: "From bounty terms to transaction statuses, we strive for clarity and transparency. No hidden fees, no ambiguous processes – just straightforward, honest interactions."
  },
  {
    icon: PhHeart,
    title: 'Human-Centric Design',
    description: "Technology should serve people, not the other way around. Our platform is designed to be intuitive, approachable, and even delightful to use, making complex interactions feel simple and secure."
  },
]);

onMounted(() => {
  // AOS or other animation initializations if needed
});
</script>

<style scoped lang="scss">
.manifesto-page {
  // Backgrounds and base styles are handled by Tailwind and global CSS
}

.animation-delay-1000 { animation-delay: 1000ms; }
.animate-pulse-glow-once {
  animation: pulseGlowEffect 2s 1s 1 ease-in-out forwards;
}

@keyframes pulseGlowEffect {
  0% { box-shadow: 0 0 0 0 rgba(127, 90, 240, 0.7); transform: scale(1); }
  50% { box-shadow: 0 0 20px 10px rgba(127, 90, 240, 0.3); transform: scale(1.02); }
  100% { box-shadow: 0 0 0 0 rgba(127, 90, 240, 0); transform: scale(1); }
}

// Ensure animations from animations.css or tailwind.config.js are available
// .animate-fade-in-up is assumed to be globally defined
</style>
