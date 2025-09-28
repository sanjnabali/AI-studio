<template>
  <div class="message-content">
    <!-- Text content -->
    <div v-if="message.message_type === 'text' || !message.message_type" class="whitespace-pre-wrap">
      {{ message.content }}
    </div>

    <!-- Image content -->
    <div v-else-if="message.message_type === 'image'" class="image-message">
      <img
        v-if="message.metadata?.image_data"
        :src="message.metadata.image_data"
        :alt="message.content"
        class="max-w-full rounded-lg shadow-sm"
      />
      <div v-else class="text-gray-500 italic">
        {{ message.content }}
      </div>
    </div>

    <!-- Code content -->
    <div v-else-if="message.message_type === 'code'" class="code-message">
      <pre class="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg overflow-x-auto"><code>{{ message.content }}</code></pre>
    </div>

    <!-- Default content -->
    <div v-else class="whitespace-pre-wrap">
      {{ message.content }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message: any
  isUser: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  copy: [content: string]
  regenerate: [message: any]
}>()
</script>

<style scoped>
.message-content {
  word-wrap: break-word;
}

.image-message img {
  max-height: 400px;
  object-fit: contain;
}

.code-message pre {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.25rem;
}
</style>
