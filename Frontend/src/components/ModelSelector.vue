<!-- Frontend/src/components/ModelSelector.vue -->
<template>
  <div class="model-selector">
    <div class="space-y-4">
      <!-- Model Selection -->
      <div>
        <label class="label">
          <span class="label-text font-medium">Model</span>
        </label>
        <select 
          v-model="localConfig.model_name" 
          class="select select-bordered w-full"
          @change="emitUpdate"
        >
          <option v-for="model in availableModels" :key="model.value" :value="model.value">
            {{ model.name }}
          </option>
        </select>
      </div>

      <!-- Temperature -->
      <div>
        <label class="label">
          <span class="label-text font-medium">Temperature</span>
          <span class="label-text-alt">{{ localConfig.temperature }}</span>
        </label>
        <input 
          v-model.number="localConfig.temperature"
          type="range" 
          min="0" 
          max="2" 
          step="0.1"
          class="range range-primary"
          @input="emitUpdate"
        />
        <div class="w-full flex justify-between text-xs px-2">
          <span>Focused</span>
          <span>Balanced</span>
          <span>Creative</span>
        </div>
      </div>

      <!-- Max Tokens -->
      <div>
        <label class="label">
          <span class="label-text font-medium">Max Tokens</span>
          <span class="label-text-alt">{{ localConfig.max_tokens }}</span>
        </label>
        <input 
          v-model.number="localConfig.max_tokens"
          type="range" 
          min="50" 
          max="4000" 
          step="50"
          class="range range-primary"
          @input="emitUpdate"
        />
      </div>

      <!-- Top P -->
      <div>
        <label class="label">
          <span class="label-text font-medium">Top P</span>
          <span class="label-text-alt">{{ localConfig.top_p }}</span>
        </label>
        <input 
          v-model.number="localConfig.top_p"
          type="range" 
          min="0" 
          max="1" 
          step="0.1"
          class="range range-primary"
          @input="emitUpdate"
        />
      </div>

      <!-- Top K -->
      <div>
        <label class="label">
          <span class="label-text font-medium">Top K</span>
          <span class="label-text-alt">{{ localConfig.top_k }}</span>
        </label>
        <input 
          v-model.number="localConfig.top_k"
          type="range" 
          min="1" 
          max="100" 
          step="1"
          class="range range-primary"
          @input="emitUpdate"
        />
      </div>

      <!-- Advanced Settings Toggle -->
      <div>
        <label class="cursor-pointer label">
          <span class="label-text">Show advanced settings</span>
          <input 
            v-model="showAdvanced" 
            type="checkbox" 
            class="checkbox checkbox-primary" 
          />
        </label>
      </div>

      <!-- Advanced Settings -->
      <div v-if="showAdvanced" class="space-y-4 border-t pt-4">
        <!-- Frequency Penalty -->
        <div>
          <label class="label">
            <span class="label-text font-medium">Frequency Penalty</span>
            <span class="label-text-alt">{{ localConfig.frequency_penalty }}</span>
          </label>
          <input 
            v-model.number="localConfig.frequency_penalty"
            type="range" 
            min="-2" 
            max="2" 
            step="0.1"
            class="range range-secondary"
            @input="emitUpdate"
          />
        </div>

        <!-- Presence Penalty -->
        <div>
          <label class="label">
            <span class="label-text font-medium">Presence Penalty</span>
            <span class="label-text-alt">{{ localConfig.presence_penalty }}</span>
          </label>
          <input 
            v-model.number="localConfig.presence_penalty"
            type="range" 
            min="-2" 
            max="2" 
            step="0.1"
            class="range range-secondary"
            @input="emitUpdate"
          />
        </div>
      </div>

      <!-- Preset Buttons -->
      <div class="grid grid-cols-3 gap-2 pt-4 border-t">
        <button 
          @click="applyPreset('creative')" 
          class="btn btn-outline btn-sm"
        >
          Creative
        </button>
        <button 
          @click="applyPreset('balanced')" 
          class="btn btn-outline btn-sm"
        >
          Balanced
        </button>
        <button 
          @click="applyPreset('precise')" 
          class="btn btn-outline btn-sm"
        >
          Precise
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { ModelSettings } from '../types'

interface Props {
  modelConfig: ModelSettings
}

const props = defineProps<Props>()

const emit = defineEmits<{
  update: [config: ModelSettings]
}>()

const showAdvanced = ref(false)

const localConfig = reactive({ ...props.modelConfig })

const availableModels = computed(() => [
  { name: 'DialoGPT Medium', value: 'microsoft/DialoGPT-medium' },
  { name: 'DialoGPT Small', value: 'microsoft/DialoGPT-small' },
  { name: 'CodeBERT Base', value: 'microsoft/CodeBERT-base' },
  { name: 'BART CNN', value: 'facebook/bart-large-cnn' }
])

const emitUpdate = () => {
  emit('update', { ...localConfig })
}

const applyPreset = (preset: 'creative' | 'balanced' | 'precise') => {
  switch (preset) {
    case 'creative':
      Object.assign(localConfig, {
        temperature: 1.2,
        top_p: 0.95,
        top_k: 80,
        frequency_penalty: 0.5,
        presence_penalty: 0.3
      })
      break
    case 'balanced':
      Object.assign(localConfig, {
        temperature: 0.7,
        top_p: 0.9,
        top_k: 50,
        frequency_penalty: 0.0,
        presence_penalty: 0.0
      })
      break
    case 'precise':
      Object.assign(localConfig, {
        temperature: 0.3,
        top_p: 0.8,
        top_k: 20,
        frequency_penalty: 0.0,
        presence_penalty: 0.0
      })
      break
  }
  emitUpdate()
}
</script>
