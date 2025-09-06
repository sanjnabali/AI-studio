<template>
  <div class="chat-window">
    <div class="messages">
      <div
        v-for="(msg, index) in currentMessages"
        :key="index"
        :class="['message', msg.role]"
      >
        <strong>{{ msg.role === 'user' ? 'You' : 'Bot' }}:</strong>
        {{ msg.content }}
      </div>
    </div>

    <div class="input-box">
      <input
        v-model="newMessage"
        type="text"
        placeholder="Type your message..."
        @keyup.enter="handleSend"
      />
      <button @click="handleSend">Send</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useChatStore } from "../store/chat";

const chatStore = useChatStore();
const newMessage = ref("");

// Helper to get messages of the first chat (or active chat if you have that logic)
const currentMessages = computed(() => {
  // If you have an activeChatId, use that to find the chat, otherwise use the first chat
  const chats = Array.isArray(chatStore.chats) ? chatStore.chats : [];
  return chats.length > 0 ? chats[0].messages : [];
});

const handleSend = async () => {
  if (!newMessage.value.trim()) return;
  // Push to the messages array of the first chat (or active chat)
  const chats = Array.isArray(chatStore.chats) ? chatStore.chats : [];
  if (chats.length > 0) {
    chats[0].messages.push({
      id: crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substr(2, 9),
      role: "user",
      content: newMessage.value,
      timestamp: new Date(),
      type: "text",
      metadata: {}
    });
  }
  newMessage.value = "";
};


</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.message {
  margin: 5px 0;
  padding: 8px 12px;
  border-radius: 8px;
}

.message.user {
  background-color: #e0f7fa;
  align-self: flex-end;
}

.message.bot {
  background-color: #f1f1f1;
  align-self: flex-start;
}

.input-box {
  display: flex;
  border-top: 1px solid #ccc;
  padding: 10px;
}

input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  margin-left: 10px;
  padding: 8px 12px;
}
</style>
