<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Sidebar -->
    <div class="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-xl font-semibold text-gray-900 dark:text-white">AI Studio</h1>
          <button
            @click="createNewChat"
            class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="New Chat"
          >
            <PlusIcon class="w-5 h-5" />
          </button>
        </div>
        
        <!-- Quick Actions -->
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="action in quickActions"
            :key="action.id"
            @click="selectQuickAction(action)"
            class="flex flex-col items-center p-2 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-center transition-colors"
            :class="{ 'bg-blue-100 dark:bg-blue-900/20 text-blue-600': selectedAction === action.id }"
          >
            <component :is="action.icon" class="w-4 h-4 mb-1" />
            {{ action.name }}
          </button>
        </div>
      </div>

      <!-- Chat List -->
      <div class="flex-1 overflow-y-auto p-4">
        <div class="space-y-2">
          <div
            v-for="chat in chatStore.chats"
            :key="chat.id"
            class="group relative"
          >
            <div
              @click="chatStore.selectChat(chat.id)"
              class="p-3 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              :class="{
                'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500': chatStore.activeChat?.id === chat.id
              }"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-gray-900 dark:text-white text-sm truncate">
                    {{ chat.title }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center space-x-2">
                    <span>{{ formatDate(chat.updated) }}</span>
                    <span>•</span>
                    <span>{{ chat.messages.length }} msgs</span>
                  </div>
                </div>
                
                <!-- Chat Actions -->
                <div class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-1">
                  <button
                    @click.stop="editChatTitle(chat)"
                    class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded"
                    title="Edit Title"
                  >
                    <PencilIcon class="w-3 h-3" />
                  </button>
                  <button
                    @click.stop="deleteChat(chat.id)"
                    class="p-1 text-gray-400 hover:text-red-600 rounded"
                    title="Delete Chat"
                  >
                    <TrashIcon class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-if="!chatStore.chats.length" class="text-center py-8">
            <ChatBubbleLeftRightIcon class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
            <p class="text-sm text-gray-500 dark:text-gray-400">No conversations yet</p>
            <button
              @click="createNewChat"
              class="mt-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
            >
              Start your first chat
            </button>
          </div>
        </div>
      </div>

      <!-- Settings Panel Toggle -->
      <div class="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="showSettings = !showSettings"
          class="w-full p-2 text-left text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg flex items-center justify-between transition-colors"
        >
          <div class="flex items-center space-x-2">
            <CogIcon class="w-4 h-4" />
            <span>Settings</span>
          </div>
          <ChevronRightIcon 
            class="w-4 h-4 transition-transform"
            :class="{ 'rotate-90': showSettings }"
          />
        </button>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col">
      <!-- Chat Header -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <SparklesIcon class="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 class="font-semibold text-gray-900 dark:text-white">
                {{ chatStore.activeChat?.title || 'New Chat' }}
              </h2>
              <p class="text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-2">
                <span>{{ currentModel }}</span>
                <span>•</span>
                <span class="flex items-center space-x-1">
                  <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Connected</span>
                </span>
              </p>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <!-- Model Selector -->
            <ModelSelector 
              v-model:selectedModel="currentModel" 
              @update:selectedModel="onModelChange"
            />

            <!-- Feature Toggles -->
            <div class="flex items-center space-x-1 border-l border-gray-200 dark:border-gray-700 pl-2">
              <!-- Canvas Toggle -->
              <button
                @click="showCanvas = !showCanvas"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                :class="{ 'bg-blue-100 dark:bg-blue-900/20 text-blue-600': showCanvas }"
                title="Toggle Code Canvas"
              >
                <CodeBracketIcon class="w-5 h-5" />
              </button>

              <!-- Voice Toggle -->
              <button
                @click="toggleVoice"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                :class="{ 'bg-red-100 dark:bg-red-900/20 text-red-600': isRecording }"
                title="Voice Input"
              >
                <MicrophoneIcon class="w-5 h-5" />
              </button>

              <!-- Audio Overview -->
              <button
                @click="generateAudioOverview"
                :disabled="!chatStore.activeChat?.messages.length"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Generate Audio Overview"
              >
                <SpeakerWaveIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="flex-1 flex">
        <!-- Messages Area -->
        <div class="flex-1 flex flex-col">
          <!-- Messages -->
          <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-6">
            <!-- Welcome Message -->
            <div v-if="!chatStore.activeChatMessages.length" class="text-center py-12">
              <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <SparklesIcon class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Welcome to AI Studio
              </h3>
              <p class="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
                Your multimodal AI workspace for coding, analysis, creative writing, and more. 
                What would you like to create today?
              </p>
              
              <!-- Feature Highlights -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
                <div
                  v-for="feature in features"
                  :key="feature.name"
                  class="p-4 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer"
                  @click="selectFeature(feature)"
                >
                  <component :is="feature.icon" class="w-8 h-8 text-blue-500 mx-auto mb-2" />
                  <div class="text-sm font-medium text-gray-900 dark:text-white">{{ feature.name }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ feature.description }}</div>
                </div>
              </div>
            </div>

            <!-- Chat Messages -->
            <div
              v-for="message in chatStore.activeChatMessages"
              :key="message.id"
              class="flex"
              :class="{
                'justify-end': message.role === 'user',
                'justify-start': message.role === 'assistant'
              }"
            >
              <div
                class="max-w-4xl group relative"
                :class="{
                  'ml-12': message.role === 'user',
                  'mr-12': message.role === 'assistant'
                }"
              >
                <!-- Message Content -->
                <div
                  class="px-4 py-3 rounded-2xl shadow-sm"
                  :class="{
                    'bg-blue-500 text-white': message.role === 'user',
                    'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700': message.role === 'assistant'
                  }"
                >
                  <!-- Text Content -->
                  <div v-if="message.type === 'text'" class="whitespace-pre-wrap">
                    {{ message.content }}
                  </div>
                  
                  <!-- Code Content -->
                  <div v-else-if="message.type === 'code'" class="space-y-3">
                    <div class="flex items-center justify-between">
                      <span class="text-xs font-medium opacity-75">{{ message.metadata?.language || 'Code' }}</span>
                      <button
                        @click="copyToClipboard(message.content)"
                        class="text-xs opacity-75 hover:opacity-100 px-2 py-1 rounded transition-opacity"
                      >
                        Copy
                      </button>
                    </div>
                    <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm font-mono"><code>{{ message.content }}</code></pre>
                  </div>
                  
                  <!-- Image Content -->
                  <div v-else-if="message.type === 'image'" class="space-y-2">
                    <img 
                      :src="message.content" 
                      :alt="message.metadata?.alt || 'Generated image'"
                      class="max-w-full h-auto rounded-lg"
                    />
                    <div v-if="message.metadata?.prompt" class="text-sm opacity-75">
                      Prompt: {{ message.metadata.prompt }}
                    </div>
                  </div>
                  
                  <!-- Audio Content -->
                  <div v-else-if="message.type === 'audio'" class="space-y-2">
                    <audio controls class="w-full">
                      <source :src="message.content" type="audio/wav">
                      Your browser does not support the audio element.
                    </audio>
                    <div v-if="message.metadata?.transcript" class="text-sm opacity-75">
                      "{{ message.metadata.transcript }}"
                    </div>
                  </div>

                  <!-- Message Metadata -->
                  <div class="flex items-center justify-between mt-2 text-xs opacity-70">
                    <span>{{ formatTime(message.timestamp) }}</span>
                    <div class="flex items-center space-x-2">
                      <span v-if="message.metadata?.model">{{ message.metadata.model }}</span>
                      <span v-if="message.metadata?.tokens">{{ message.metadata.tokens }} tokens</span>
                    </div>
                  </div>
                </div>

                <!-- Message Actions -->
                <div 
                  v-if="message.role === 'assistant'"
                  class="absolute -bottom-2 left-4 opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-1"
                >
                  <button
                    @click="regenerateResponse(message)"
                    class="p-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full shadow-sm hover:shadow-md transition-shadow"
                    title="Regenerate"
                  >
                    <ArrowPathIcon class="w-3 h-3 text-gray-600 dark:text-gray-400" />
                  </button>
                  <button
                    @click="copyToClipboard(message.content)"
                    class="p-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full shadow-sm hover:shadow-md transition-shadow"
                    title="Copy"
                  >
                    <ClipboardIcon class="w-3 h-3 text-gray-600 dark:text-gray-400" />
                  </button>
                  <button
                    @click="shareMessage(message)"
                    class="p-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full shadow-sm hover:shadow-md transition-shadow"
                    title="Share"
                  >
                    <ShareIcon class="w-3 h-3 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Typing Indicator -->
            <div v-if="chatStore.loading" class="flex justify-start">
              <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 shadow-sm">
                <div class="flex items-center space-x-2">
                  <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  </div>
                  <span class="text-sm text-gray-500 dark:text-gray-400">AI is thinking...</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Input Area -->
          <div class="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <!-- File Upload Area -->
            <div v-if="uploadedFiles.length" class="mb-4">
              <div class="flex flex-wrap gap-2">
                <div
                  v-for="file in uploadedFiles"
                  :key="file.name"
                  class="flex items-center space-x-2 bg-gray-100 dark:bg-gray-700 rounded-lg px-3 py-2"
                >
                  <component :is="getFileIcon(file.type)" class="w-4 h-4 text-gray-500" />
                  <span class="text-sm text-gray-700 dark:text-gray-300 truncate max-w-32">{{ file.name }}</span>
                  <button
                    @click="removeFile(file.name)"
                    class="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <XMarkIcon class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Input Controls -->
            <div class="flex items-end space-x-3">
              <!-- File Upload -->
              <button
                @click="triggerFileUpload"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Upload Files"
              >
                <PaperClipIcon class="w-5 h-5" />
              </button>

              <!-- Voice Input -->
              <VoiceRecorder 
                @recordingComplete="handleVoiceInput"
                @recordingStart="onRecordingStart"
                @recordingStop="onRecordingStop"
              />

              <!-- Message Input -->
              <div class="flex-1 relative">
                <textarea
                  ref="messageInput"
                  v-model="inputMessage"
                  @keydown="handleInputKeydown"
                  @input="handleInputChange"
                  placeholder="Message AI Studio..."
                  class="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-xl bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  :rows="inputRows"
                  :disabled="chatStore.loading"
                ></textarea>
                
                <!-- Send Button -->
                <button
                  @click="sendMessage"
                  :disabled="!canSend"
                  class="absolute right-2 bottom-2 p-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                  title="Send Message"
                >
                  <PaperAirplaneIcon class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Suggestions -->
            <div v-if="showSuggestions" class="mt-4 flex flex-wrap gap-2">
              <button
                v-for="suggestion in currentSuggestions"
                :key="suggestion"
                @click="applySuggestion(suggestion)"
                class="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-full transition-colors"
              >
                {{ suggestion }}
              </button>
            </div>

            <!-- Input Status -->
            <div v-if="inputStatus" class="mt-2 text-xs text-gray-500 dark:text-gray-400 flex items-center space-x-2">
              <span>{{ inputStatus }}</span>
              <LoadingSpinner v-if="processingInput" />
            </div>
          </div>
        </div>

        <!-- Code Canvas Panel -->
        <CodeCanvas v-if="showCanvas" class="w-96" />
      </div>
    </div>

    <!-- Settings Panel -->
    <div
      v-if="showSettings"
      class="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col"
    >
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 class="font-semibold text-gray-900 dark:text-white">Model Settings</h3>
        <button
          @click="showSettings = false"
          class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded"
        >
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4 space-y-6">
        <!-- Temperature Control -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Temperature</label>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ settingsStore.modelConfig.temperature }}</span>
          </div>
          <input
            v-model.number="settingsStore.modelConfig.temperature"
            type="range"
            min="0"
            max="2"
            step="0.1"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
          <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>Precise</span>
            <span>Creative</span>
          </div>
        </div>

        <!-- Top K Control -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Top K</label>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ settingsStore.modelConfig.topK }}</span>
          </div>
          <input
            v-model.number="settingsStore.modelConfig.topK"
            type="range"
            min="1"
            max="100"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
        </div>

        <!-- Top P Control -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Top P</label>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ settingsStore.modelConfig.topP }}</span>
          </div>
          <input
            v-model.number="settingsStore.modelConfig.topP"
            type="range"
            min="0"
            max="1"
            step="0.01"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
        </div>

        <!-- Max Tokens -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Max Tokens</label>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ settingsStore.modelConfig.maxTokens }}</span>
          </div>
          <input
            v-model.number="settingsStore.modelConfig.maxTokens"
            type="range"
            min="256"
            max="4096"
            step="256"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
        </div>

        <!-- Domain Profiles -->
        <div>
          <h4 class="font-medium text-gray-700 dark:text-gray-300 mb-3">Domain Profiles</h4>
          <div class="space-y-2">
            <label
              v-for="profile in settingsStore.domainProfiles"
              :key="profile.id"
              class="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg cursor-pointer transition-colors"
            >
              <input
                v-model="profile.active"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-3"
              />
              <div>
                <span class="text-sm text-gray-700 dark:text-gray-300 font-medium">{{ profile.name }}</span>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  Optimized for {{ profile.id }} tasks
                </div>
              </div>
            </label>
          </div>
        </div>

        <!-- Active Agents -->
        <div>
          <h4 class="font-medium text-gray-700 dark:text-gray-300 mb-3">Active Agents</h4>
          <div class="space-y-3">
            <div
              v-for="agent in settingsStore.agents"
              :key="agent.id"
              class="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="font-medium text-sm text-gray-900 dark:text-white">
                  {{ agent.name }}
                </div>
                <div
                  class="w-2 h-2 rounded-full"
                  :class="{
                    'bg-green-500': agent.status === 'idle',
                    'bg-yellow-500': agent.status === 'busy',
                    'bg-red-500': agent.status === 'error'
                  }"
                  :title="agent.status"
                ></div>
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mb-2">
                {{ agent.description }}
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 px-2 py-1 rounded capitalize">
                  {{ agent.type }}
                </span>
                <button
                  @click="configureAgent(agent)"
                  class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                >
                  Configure
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      multiple
      accept="image/*,.pdf,.docx,.txt,.mp3,.mp4,.json,.csv"
      class="hidden"
      @change="handleFileUpload"
    />

    <!-- Edit Title Modal -->
    <div v-if="editingChat" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-96 max-w-90vw">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Edit Chat Title</h3>
        <input
          ref="titleInput"
          v-model="newTitle"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          @keydown.enter="saveChatTitle"
          @keydown.escape="cancelEditTitle"
        />
        <div class="flex justify-end space-x-2 mt-4">
          <button
            @click="cancelEditTitle"
            class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
          >
            Cancel
          </button>
          <button
            @click="saveChatTitle"
            class="px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

// Import icons (adjust import paths as needed)
import { 
  PlusIcon, PencilIcon, TrashIcon, ChatBubbleLeftRightIcon, CogIcon, ChevronRightIcon,
  SparklesIcon, CodeBracketIcon, MicrophoneIcon, SpeakerWaveIcon, PaperClipIcon,
  PaperAirplaneIcon, XMarkIcon, ArrowPathIcon, ClipboardIcon, ShareIcon
} from '@heroicons/vue/24/outline'

// Import components (adjust import paths as needed)
import ModelSelector from '@/composables/ModelSelector.vue'
import CodeCanvas from '@/composables/CodeCanvas.vue'
import VoiceRecorder from '@/composables/VoiceRecorder.vue'
import LoadingSpinner from '@/composables/LoadingSpinner.vue'

// --- Reactive State ---
const chatStore = ref({
  chats: [
    // Example chat
    // { id: 1, title: "Welcome", updated: new Date(), messages: [{id: 1, role: 'user', content: 'Hi', type: 'text', timestamp: Date.now()}] }
  ],
  activeChat: null,
  activeChatMessages: [],
  loading: false,
  selectChat(id) {
    this.activeChat = this.chats.find(c => c.id === id)
    this.activeChatMessages = this.activeChat ? this.activeChat.messages : []
  }
})

const settingsStore = ref({
  modelConfig: {
    temperature: 1,
    topK: 40,
    topP: 0.95,
    maxTokens: 1024,
  },
  domainProfiles: [
    { id: 'general', name: 'General', active: true },
    { id: 'code', name: 'Coding', active: false }
  ],
  agents: [
    { id: 1, name: 'Code Helper', status: 'idle', description: 'Helps with code', type: 'assistant' }
  ]
})

const quickActions = ref([
  { id: 'code', name: 'Code', icon: CodeBracketIcon },
  { id: 'voice', name: 'Voice', icon: MicrophoneIcon },
  { id: 'image', name: 'Image', icon: PaperClipIcon }
])
const selectedAction = ref(null)

const features = ref([
  { name: 'Code', description: 'Write and debug code', icon: CodeBracketIcon },
  { name: 'Voice', description: 'Voice input and output', icon: MicrophoneIcon },
  { name: 'Image', description: 'Generate images', icon: PaperClipIcon },
  { name: 'Chat', description: 'Conversational AI', icon: ChatBubbleLeftRightIcon }
])

const showSettings = ref(false)
const showCanvas = ref(false)
const isRecording = ref(false)
const uploadedFiles = ref([])
const inputMessage = ref('')
const inputRows = ref(2)
const canSend = computed(() => inputMessage.value.trim().length > 0 && !chatStore.value.loading)
const showSuggestions = ref(false)
const currentSuggestions = ref(['How can I help you?', 'Show me an example', 'Explain this code'])
const inputStatus = ref('')
const processingInput = ref(false)
const editingChat = ref(false)
const newTitle = ref('')
const currentModel = ref('GPT-4')
const messagesContainer = ref(null)
const messageInput = ref(null)
const fileInput = ref(null)
const titleInput = ref(null)

// --- Methods ---
function createNewChat() {
  const id = Date.now()
  const chat = {
    id,
    title: `Chat ${chatStore.value.chats.length + 1}`,
    updated: new Date(),
    messages: []
  }
  chatStore.value.chats.unshift(chat)
  chatStore.value.selectChat(id)
}

function selectQuickAction(action) {
  selectedAction.value = action.id
}

function editChatTitle(chat) {
  editingChat.value = true
  newTitle.value = chat.title
  nextTick(() => titleInput.value && titleInput.value.focus())
}

function deleteChat(id) {
  chatStore.value.chats = chatStore.value.chats.filter(c => c.id !== id)
  if (chatStore.value.activeChat?.id === id) {
    chatStore.value.activeChat = null
    chatStore.value.activeChatMessages = []
  }
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
}

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleTimeString()
}

function copyToClipboard(content) {
  navigator.clipboard.writeText(content)
}

function regenerateResponse(message) {
  // Stub: Add your logic
  alert('Regenerate response for: ' + message.content)
}

function shareMessage(message) {
  // Stub: Add your logic
  alert('Share message: ' + message.content)
}

function selectFeature(feature) {
  // Stub: Add your logic
  alert('Selected feature: ' + feature.name)
}

function getFileIcon(type) {
  // You can expand this for more types
  if (type.startsWith('image/')) return PaperClipIcon
  if (type === 'application/pdf') return PaperClipIcon
  return PaperClipIcon
}

function removeFile(name) {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.name !== name)
}

function triggerFileUpload() {
  fileInput.value && fileInput.value.click()
}

function handleFileUpload(e) {
  const files = Array.from(e.target.files)
  uploadedFiles.value.push(...files)
  e.target.value = ''
}

function handleInputKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

function handleInputChange(e) {
  inputRows.value = inputMessage.value.split('\n').length
}

function sendMessage() {
  if (!canSend.value) return
  const msg = {
    id: Date.now(),
    role: 'user',
    content: inputMessage.value,
    type: 'text',
    timestamp: Date.now()
  }
  if (chatStore.value.activeChat) {
    chatStore.value.activeChat.messages.push(msg)
    chatStore.value.activeChatMessages = chatStore.value.activeChat.messages
    chatStore.value.activeChat.updated = new Date()
  }
  inputMessage.value = ''
}

function applySuggestion(suggestion) {
  inputMessage.value = suggestion
}

function handleVoiceInput(data) {
  inputMessage.value = data.transcript || ''
}

function onRecordingStart() {
  isRecording.value = true
}

function onRecordingStop() {
  isRecording.value = false
}

function toggleVoice() {
  isRecording.value = !isRecording.value
}

function generateAudioOverview() {
  alert('Audio overview generated!')
}

function onModelChange(model) {
  currentModel.value = model
}

function saveChatTitle() {
  if (chatStore.value.activeChat) {
    chatStore.value.activeChat.title = newTitle.value
    editingChat.value = false
  }
}

function cancelEditTitle() {
  editingChat.value = false
}

function configureAgent(agent) {
  alert('Configure agent: ' + agent.name)
}

onMounted(() => {
  // Optionally scroll to bottom, focus input, etc.
})
</script>