<template>
  <div class="landing-page-container overflow-x-hidden">
    <!-- Hero Section -->
    <section class="hero-section min-h-screen flex flex-col justify-center items-center relative text-center p-4 md:p-8 noise-bg">
      <div class="absolute inset-0 bg-gradient-to-b from-obsidian-black/80 via-obsidian-black/60 to-quantum-purple/30 z-0"></div>
      <div class="absolute inset-0 opacity-10 pattern-dots"></div>

      <div class="relative z-10 animate-fade-in-up animation-delay-300">
        <ClientOnly>
          <NexusMascot :size="180" animationState="idle" class="mb-8 mx-auto" />
        </ClientOnly>
        <h1 class="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold font-display text-pure-white mb-6 shadow-text">
          Your Network is Your <span class="text-quantum-purple">Net Worth</span>.
        </h1>
        <p class="text-lg md:text-xl lg:text-2xl text-gray-300 mb-10 max-w-3xl mx-auto leading-relaxed">
          Unlock exclusive introductions and monetize your professional connections in a marketplace built on trust and value.
        </p>
        <div class="space-x-4 flex flex-col sm:flex-row justify-center items-center">
          <AppButton to="/bounties" size="large" color="quantum-purple" class="mb-4 sm:mb-0 animate-pulse-glow-once">
            <PhMagnifyingGlass class="mr-2" weight="bold" /> Find an Introduction
          </AppButton>
          <AppButton to="/auth/register?role=connector" size="large" variant="outline" color="pure-white" class="hover:!bg-pure-white/10">
            <PhLinkSimpleHorizontal class="mr-2" weight="bold" /> Become a Connector
          </AppButton>
        </div>
      </div>
      <div class="absolute bottom-10 left-1/2 transform -translate-x-1/2 animate-bounce">
        <PhArrowDown size="32" class="text-gray-400" />
      </div>
    </section>

    <!-- The Problem Section -->
    <section class="py-16 md:py-24 bg-obsidian-black/90 relative overflow-hidden">
      <div class="container mx-auto px-6 md:px-8 text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-pure-white mb-6 font-display">The <span class="text-danger-red">Chaos</span> of "Free" Networking</h2>
        <p class="text-gray-300 text-lg md:text-xl max-w-2xl mx-auto mb-12 leading-relaxed">
          Endless DMs, ghosted emails, and valuable connections lost in the noise. Your time is precious. Stop chasing, start connecting.
        </p>
        <!-- Visual Representation of Chaos (Conceptual) -->
        <div class="relative h-64 md:h-96 flex justify-center items-center">
            <div class="absolute w-full h-full opacity-20">
                <!-- Placeholder for animated icons/logos representing chaos -->
                <PhLinkedinLogo size="48" class="absolute top-1/4 left-1/4 text-gray-500 animate-float" style="animation-duration: 5s;" />
                <PhEnvelope size="40" class="absolute top-1/2 right-1/4 text-gray-600 animate-float" style="animation-duration: 6s; animation-delay: 0.5s;" />
                <PhChatDots size="44" class="absolute bottom-1/4 left-1/3 text-gray-500 animate-float" style="animation-duration: 4s; animation-delay: 1s;" />
                 <PhSpinnerGap size="52" class="absolute top-1/3 right-1/3 text-gray-600 animate-spin-slow" />
            </div>
           <p class="text-2xl text-quantum-purple/50 font-semibold z-10 bg-obsidian-black/70 p-4 rounded-lg shadow-lg">Lost Opportunities & Wasted Time</p>
        </div>
      </div>
    </section>

    <!-- The Solution Section -->
    <section class="py-16 md:py-24 bg-gradient-to-br from-quantum-purple/10 via-obsidian-black to-obsidian-black relative">
       <div class="absolute inset-0 opacity-5 pattern-grid"></div>
      <div class="container mx-auto px-6 md:px-8">
        <h2 class="text-3xl md:text-4xl font-bold text-pure-white mb-16 text-center font-display">The <span class="text-guardian-green">Solution</span>: Order & Value</h2>
        <div class="grid md:grid-cols-3 gap-8 md:gap-12">
          <GlassCard class="text-center" data-aos="fade-up" data-aos-delay="100" :interactiveGlow="true">
            <template #header>
              <PhTarget size="48" class="text-quantum-purple mx-auto mb-4" weight="duotone" />
              <h3 class="text-xl font-semibold text-pure-white mb-2">Post a Bounty</h3>
            </template>
            <p class="text-gray-300 text-sm leading-relaxed">Clearly define your need for an introduction. Set a fair price for the value you seek. Attract motivated Connectors.</p>
          </GlassCard>
          <GlassCard class="text-center" data-aos="fade-up" data-aos-delay="200" :interactiveGlow="true">
            <template #header>
              <PhShieldCheck size="48" class="text-quantum-purple mx-auto mb-4" weight="duotone" />
              <h3 class="text-xl font-semibold text-pure-white mb-2">Secure Escrow</h3>
            </template>
            <p class="text-gray-300 text-sm leading-relaxed">Funds are held securely in escrow. Connectors are incentivized to deliver quality introductions. Peace of mind for everyone.</p>
          </GlassCard>
          <GlassCard class="text-center" data-aos="fade-up" data-aos-delay="300" :interactiveGlow="true">
            <template #header>
              <PhSparkle size="48" class="text-quantum-purple mx-auto mb-4" weight="duotone" />
              <h3 class="text-xl font-semibold text-pure-white mb-2">Unlock Introductions</h3>
            </template>
            <p class="text-gray-300 text-sm leading-relaxed">Receive valuable introductions. Confirm the connection. Funds are released upon successful linkage. Simple, transparent, effective.</p>
          </GlassCard>
        </div>
         <div class="text-center mt-16">
            <AppButton to="/manifesto" size="large" variant="outline" color="quantum-purple">
                Learn More About Our Vision <PhArrowRight class="ml-2" />
            </AppButton>
        </div>
      </div>
    </section>

    <!-- Our Story / Founder Section -->
    <section class="py-16 md:py-24 bg-obsidian-black relative">
      <div class="container mx-auto px-6 md:px-8">
        <div class="flex flex-col md:flex-row items-center md:space-x-12">
          <div class="md:w-1/2 mb-8 md:mb-0" data-aos="fade-right">
            <h2 class="text-3xl md:text-4xl font-bold text-pure-white mb-6 font-display">Crafted with <span class="text-quantum-purple">Purpose</span></h2>
            <p class="text-gray-300 text-lg mb-4 leading-relaxed">
              The Access Marketplace was born from a simple realization: true professional networking is about quality, not quantity. In a world saturated with superficial connections, we're building a platform where every introduction has tangible value.
            </p>
            <p class="text-gray-300 text-lg mb-6 leading-relaxed">
              Our founder, [Founder's Name/A Visionary Team], experienced firsthand the frustrations of inefficient networking and the immense power of a single, well-placed introduction. This platform is our commitment to making high-value connections accessible and rewarding for everyone involved.
            </p>
            <NuxtLink to="/about-us" class="text-quantum-purple font-semibold hover:underline">
              Meet the Team & Our Full Story <PhUsersThree class="inline ml-1" />
            </NuxtLink>
          </div>
          <div class="md:w-1/2" data-aos="fade-left">
            <img src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80" alt="Founder/Team Placeholder" class="rounded-xl shadow-2xl object-cover w-full h-80 md:h-96 glass-effect p-1">
            <!-- Replace with actual founder/team image -->
          </div>
        </div>
      </div>
    </section>

    <!-- Call to Action -->
    <section class="py-16 md:py-24 bg-quantum-purple/80 text-center relative noise-bg">
       <div class="absolute inset-0 bg-gradient-to-br from-quantum-purple/80 via-purple-800 to-obsidian-black/50 opacity-50 z-0"></div>
      <div class="container mx-auto px-6 md:px-8 relative z-10">
        <h2 class="text-3xl md:text-4xl font-bold text-pure-white mb-6 font-display">Ready to Transform Your Network?</h2>
        <p class="text-gray-200 text-lg md:text-xl max-w-xl mx-auto mb-10 leading-relaxed">
          Join The Access Marketplace today and experience the future of professional connections.
        </p>
        <AppButton to="/auth/register" size="large" color="pure-white" class="!text-quantum-purple animate-pulse-glow-once">
          Get Started Now <PhRocketLaunch class="ml-2" weight="bold" />
        </AppButton>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  PhMagnifyingGlass, PhLinkSimpleHorizontal, PhArrowDown, PhTarget, PhShieldCheck, PhSparkle, PhUsersThree, PhRocketLaunch,
  PhLinkedinLogo, PhEnvelope, PhChatDots, PhSpinnerGap, PhArrowRight
} from 'phosphor-vue';
import NexusMascot from '~/components/NexusMascot.vue'; // Ensure path is correct
import AppButton from '~/components/ui/AppButton.vue';
import GlassCard from '~/components/ui/GlassCard.vue';

definePageMeta({
  layout: 'landing',
  // Optional: control header/footer visibility for this specific page
  // showHeader: false,
  // showFooter: true,
});

useHead({
  title: 'The Access Marketplace - Unlock Your Network',
  meta: [
    { name: 'description', content: 'Connect with high-value individuals and monetize your professional network. Post bounties, make introductions, and build meaningful connections securely.' },
    { property: 'og:title', content: 'The Access Marketplace - Unlock Your Network' },
    { property: 'og:description', content: 'A new era of professional networking where value and trust come first.' },
    { property: 'og:image', content: '/og-image-landing.jpg' }, // Create an engaging OG image
    { name: 'twitter:card', content: 'summary_large_image' },
  ],
});

onMounted(async () => {
  if (process.client) {
    // Initialize AOS (Animate On Scroll) if you added it
    // Make sure to install and import 'aos'
    // e.g. import AOS from 'aos'; import 'aos/dist/aos.css';
    // AOS.init({
    //   duration: 700,
    //   easing: 'ease-out-cubic',
    //   once: true,
    //   offset: 50,
    // });

    // Lenis smooth scroll is initialized in app.vue or a plugin
  }
});
</script>

<style scoped lang="scss">
.landing-page-container {
  // Ensures that the page uses the full width and avoids horizontal scroll issues.
}

.hero-section {
  // background: url('/path-to-subtle-hero-background.jpg') no-repeat center center;
  // background-size: cover;
  // This is now handled by the gradient div and noise-bg class
}

.shadow-text {
  text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.3), 0px 0px 20px rgba(127, 90, 240, 0.3);
}

.pattern-dots {
  background-image: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}
.pattern-grid {
    background-image:
        linear-gradient(to right, rgba(127, 90, 240, 0.05) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(127, 90, 240, 0.05) 1px, transparent 1px);
    background-size: 40px 40px;
}


/* Animation for pulsing button */
.animate-pulse-glow-once {
  animation: pulseGlowEffect 2s 1s 1 ease-in-out forwards; /* 1s delay, runs once */
}

@keyframes pulseGlowEffect {
  0% { box-shadow: 0 0 0 0 rgba(127, 90, 240, 0.7); transform: scale(1); }
  50% { box-shadow: 0 0 20px 10px rgba(127, 90, 240, 0.3); transform: scale(1.02); }
  100% { box-shadow: 0 0 0 0 rgba(127, 90, 240, 0); transform: scale(1); }
}

/* Animation for chaos icons */
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}
.animate-float {
  animation-name: float;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
}

@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.animate-spin-slow {
  animation: spin-slow 10s linear infinite;
}


/* General animation delays for staggered effect */
.animation-delay-300 { animation-delay: 0.3s; }
.animation-delay-500 { animation-delay: 0.5s; }
.animation-delay-700 { animation-delay: 0.7s; }

/* Ensure AOS animations are visible if used */
[data-aos] {
  opacity: 0; // Start hidden for AOS
  transition-property: transform, opacity; // AOS will animate these
}
</style>
