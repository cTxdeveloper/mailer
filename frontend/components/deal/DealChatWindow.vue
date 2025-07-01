<template>
  <GlassCard class="deal-chat-window flex flex-col h-[calc(100vh-200px)] md:h-[600px]" padding="p-0">
    <header class="p-4 border-b border-white/10 flex justify-between items-center bg-obsidian-black/30 rounded-t-xl">
      <h2 class="text-lg font-semibold text-pure-white font-display">Secure Communication Channel</h2>
      <div class="flex items-center text-xs text-gray-400">
        <PhLockSimple class="mr-1.5 text-guardian-green" weight="bold" />
        End-to-end encrypted (simulated)
      </div>
    </header>

    <div ref="messagesContainer" class="flex-grow overflow-y-auto p-4 space-y-4 bg-obsidian-black/10 custom-scrollbar">
      <UiAppLoader v-if="pending && !messages.length" message="Loading messages..." inline />
      <div v-if="!pending && !messages.length" class="text-center text-gray-500 py-10">
        <PhChatCircleDots size="48" class="mx-auto mb-2 opacity-50" />
        No messages yet. Start the conversation!
      </div>
      <div v-for="message in messages" :key="message.id" class="chat-message-group" :class="{ 'is-sender': message.senderId === authStore.user?.id }">
        <div class="message-bubble" :class="{ 'bg-quantum-purple text-pure-white': message.senderId === authStore.user?.id, 'bg-gray-700/70 text-gray-200': message.senderId !== authStore.user?.id }">
          <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ message.content }}</p>
        </div>
        <div class="message-meta text-xs mt-1" :class="{ 'text-right': message.senderId === authStore.user?.id, 'text-left': message.senderId !== authStore.user?.id }">
          <span class="text-gray-500" :title="dayjs(message.createdAt).format('MMM D, YYYY h:mm A')">
            {{ dayjs(message.createdAt).fromNow() }}
          </span>
          <span v-if="message.senderId !== authStore.user?.id" class="text-gray-400 font-medium ml-1">
            - {{ message.sender?.displayName || 'Participant' }}
          </span>
           <PhCheckCircle v-if="message.senderId === authStore.user?.id && message.isRead" size="14" class="inline ml-1 text-blue-400" title="Read" />
           <PhCircleNotch v-else-if="message.senderId === authStore.user?.id && !message.isDelivered_temp" size="14" class="inline ml-1 text-gray-500 animate-spin" title="Sending..." />
           <PhCheck v-else-if="message.senderId === authStore.user?.id && message.isDelivered_temp && !message.isRead" size="14" class="inline ml-1 text-gray-400" title="Delivered" />

        </div>
      </div>
    </div>

    <footer class="p-3 border-t border-white/10 bg-obsidian-black/30 rounded-b-xl">
      <form @submit.prevent="sendMessage" class="flex items-center space-x-3">
        <UiFormTextarea
          v-model="newMessageContent"
          name="chatMessage"
          placeholder="Type your message here... (Shift+Enter for new line)"
          class="flex-grow !mb-0"
          :rows="1"
          @keydown.enter.exact.prevent="sendMessage"
          :disabled="isSending || !canSendMessage"
          input-class="!py-2.5 !pr-10"
          :style="{ maxHeight: '120px', overflowY: 'auto' }"
        />
        <AppButton type="submit" color="quantum-purple" class="!p-2.5" :loading="isSending" :disabled="isSending || !newMessageContent.trim() || !canSendMessage" aria-label="Send Message">
          <PhPaperPlaneRight size="20" weight="fill" />
        </AppButton>
      </form>
      <p v-if="!canSendMessage" class="text-xs text-yellow-500/80 mt-1.5 text-center">
        Messaging is disabled as the deal is {{ deal?.status }}.
      </p>
    </footer>
  </GlassCard>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, computed } from 'vue';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
dayjs.extend(relativeTime);

import { PhLockSimple, PhPaperPlaneRight, PhChatCircleDots, PhCheck, PhCheckCircle, PhCircleNotch } from 'phosphor-vue';
import type { Deal, Message, User } from '~/types';
import { useApiFetch } from '~/composables/useApiFetch';
import { useAuthStore } from '~/store/auth';
import { useUiStore } from '~/store/ui';
import GlassCard from '~/components/ui/GlassCard.vue';
import UiAppLoader from '~/components/ui/AppLoader.vue';
import UiFormTextarea from '~/components/ui/FormTextarea.vue';
import AppButton from '~/components/ui/AppButton.vue';

const props = defineProps<{
  dealId: string;
  deal: Deal | null; // Pass the deal object for status checks
}>();

const emit = defineEmits(['message-posted']);

const authStore = useAuthStore();
const uiStore = useUiStore();

const messages = ref<Message[]>([]);
const newMessageContent = ref('');
const messagesContainer = ref<HTMLElement | null>(null);
const isSending = ref(false);
const pollingInterval = ref<ReturnType<typeof setInterval> | null>(null);


const { data: fetchedMessages, pending, error, refresh: fetchMessages } = await useApiFetch<Message[]>(`/deals/${props.dealId}/messages`);

watch(fetchedMessages, (newVal) => {
  if (newVal) {
    // Sort messages by createdAt if not already sorted by backend
    messages.value = newVal.sort((a, b) => dayjs(a.createdAt).valueOf() - dayjs(b.createdAt).valueOf());
    scrollToBottom();
  }
}, { immediate: true });


const canSendMessage = computed(() => {
    if (!props.deal) return false;
    // Allow messaging unless deal is completed, cancelled, or disputed (unless dispute resolution involves chat)
    return !['completed', 'cancelled', 'disputed'].includes(props.deal.status.toLowerCase());
});

const sendMessage = async () => {
  if (!newMessageContent.value.trim() || !canSendMessage.value) return;

  isSending.value = true;
  const tempMessageId = `temp_${Date.now()}`; // For optimistic update

  // Optimistic update
  const optimisticMessage: Message = {
    id: tempMessageId,
    dealId: props.dealId,
    senderId: authStore.user!.id, // Assume user is authenticated
    sender: authStore.user as User, // Cast for optimistic display
    content: newMessageContent.value.trim(),
    createdAt: new Date().toISOString(),
    isRead: false,
    isDelivered_temp: false, // Temporary flag for UI
  };
  messages.value.push(optimisticMessage);
  const currentMessageContent = newMessageContent.value;
  newMessageContent.value = ''; // Clear input immediately
  scrollToBottom();

  try {
    const { data: sentMessage, error: sendError } = await useApiFetch<Message>(`/deals/${props.dealId}/messages`, {
      method: 'POST',
      body: { content: currentMessageContent.trim() },
    });

    if (sendError.value) throw sendError.value;

    if (sentMessage.value) {
      // Replace optimistic message with actual message from server
      const index = messages.value.findIndex(m => m.id === tempMessageId);
      if (index !== -1) {
        messages.value.splice(index, 1, sentMessage.value);
      } else {
        // If not found (shouldn't happen), just add it
        messages.value.push(sentMessage.value);
      }
      emit('message-posted', sentMessage.value);
    } else {
        // Revert optimistic update on failure if no message returned
        const index = messages.value.findIndex(m => m.id === tempMessageId);
        if (index !== -1) messages.value.splice(index, 1);
        newMessageContent.value = currentMessageContent; // Restore content
    }

  } catch (e: any) {
    // console.error('Failed to send message:', e);
    // uiStore.showToast(e.message || 'Failed to send message.', 'error');
    // Revert optimistic update
    const index = messages.value.findIndex(m => m.id === tempMessageId);
    if (index !== -1) messages.value.splice(index, 1);
    newMessageContent.value = currentMessageContent; // Restore content
  } finally {
    isSending.value = false;
    scrollToBottom(); // Ensure scroll after potential message height change
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// Polling for new messages (simple implementation)
// A WebSocket connection would be better for real-time chat.
const startPolling = () => {
  if (pollingInterval.value) clearInterval(pollingInterval.value);
  pollingInterval.value = setInterval(async () => {
    // Only fetch if user is active on the page (basic check)
    if (document.hidden) return;
    try {
      // Fetch only new messages if API supports it (e.g., using last message timestamp)
      // For simplicity, re-fetching all and letting watcher handle updates.
      await fetchMessages();
    } catch (e) {
      console.warn("Chat polling error:", e);
    }
  }, 5000); // Poll every 5 seconds
};

const stopPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
    pollingInterval.value = null;
  }
};

onMounted(() => {
  scrollToBottom();
  if (canSendMessage.value) { // Only poll if chat is active
      startPolling();
  }
});

onUnmounted(() => {
  stopPolling();
});

watch(() => props.dealId, (newDealId, oldDealId) => {
    if (newDealId !== oldDealId) {
        messages.value = []; // Clear messages for new deal
        stopPolling();
        fetchMessages(); // Fetch messages for the new deal
        if (canSendMessage.value) {
            startPolling();
        }
    }
});

watch(canSendMessage, (canSend) => {
    if (canSend) {
        startPolling();
    } else {
        stopPolling();
    }
});

</script>

<style scoped lang="scss">
.deal-chat-window {
  // Max height is set inline, can be adjusted via props or more complex CSS
}

.custom-scrollbar {
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(127, 90, 240, 0.5); // Quantum Purple scrollbar
    border-radius: 3px;
  }
  &::-webkit-scrollbar-thumb:hover {
    background: rgba(127, 90, 240, 0.8);
  }
}

.chat-message-group {
  display: flex;
  flex-direction: column;
  &.is-sender {
    align-items: flex-end;
  }
  &:not(.is-sender) {
    align-items: flex-start;
  }
}

.message-bubble {
  max-width: 75%;
  padding: 0.6rem 0.9rem;
  border-radius: 1rem;
  word-wrap: break-word;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);

  &.is-sender { // This class should be on message-bubble if used like this
    // border-bottom-right-radius: 0.25rem; This is for tail style
  }
  &:not(.is-sender) { // This class should be on message-bubble if used like this
    // border-bottom-left-radius: 0.25rem;
  }
}

// Adjust textarea height dynamically (basic example, might need more robust solution)
// The form-input-base class in UiFormTextarea might need `resize: none` and `overflow: hidden`
// for this to work well with JS height adjustment.
// For now, using browser default textarea scroll with max-height.
</style>
