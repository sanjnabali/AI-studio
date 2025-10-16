<!-- Frontend/src/components/ModelSelector.vue -->
<template>
  <div class="model-selector bg-opacity-20 bg-orange-50 backdrop-blur-md rounded-xl p-6 shadow-lg border border-orange-100/20">
    <div class="space-y-4">
      <!-- Model Selection -->
      <div>
        <label class="label">
          <span class="label-text font-medium text-orange-900">Model</span>
        </label>
        <select 
          v-model="localConfig.model_name" 
          class="select w-full bg-white/50 backdrop-blur-sm border-orange-200 hover:border-orange-300 focus:border-orange-400 rounded-lg shadow-sm"
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
          <span class="label-text font-medium text-orange-900">Temperature</span>
          <span class="label-text-alt text-orange-600">{{ localConfig.temperature }}</span>
        </label>
        <input 
          v-model.number="localConfig.temperature"
          type="range" 
          min="0" 
          max="2" 
          step="0.1"
          class="range bg-orange-100 [--range-shdw:theme(colors.orange.200)] hover:[--range-shdw:theme(colors.orange.300)] [&::-webkit-slider-thumb]:bg-orange-500 [&::-webkit-slider-thumb]:hover:bg-orange-600"
          @input="emitUpdate"
        />
        <div class="w-full flex justify-between text-xs px-2 text-orange-700 mt-1">
          <span>Focused</span>
          <span>Balanced</span>
          <span>Creative</span>
        </div>
      </div>

      <!-- Max Tokens -->
      <div>
        <label class="label">
          <span class="label-text font-medium text-orange-900">Max Tokens</span>
          <span class="label-text-alt text-orange-600">{{ localConfig.max_tokens }}</span>
        </label>
        <input 
          v-model.number="localConfig.max_tokens"
          type="range" 
          min="50" 
          max="4000" 
          step="50"
          class="range bg-orange-100 [--range-shdw:theme(colors.orange.200)] hover:[--range-shdw:theme(colors.orange.300)] [&::-webkit-slider-thumb]:bg-orange-500 [&::-webkit-slider-thumb]:hover:bg-orange-600"
          @input="emitUpdate"
        />
      </div>

      <!-- Top P -->
      <div>
        <label class="label">
          <span class="label-text font-medium text-orange-900">Top P</span>
          <span class="label-text-alt text-orange-600">{{ localConfig.top_p }}</span>
        </label>
        <input 
          v-model.number="localConfig.top_p"
          type="range" 
          min="0" 
          max="1" 
          step="0.1"
          class="range bg-orange-100 [--range-shdw:theme(colors.orange.200)] hover:[--range-shdw:theme(colors.orange.300)] [&::-webkit-slider-thumb]:bg-orange-500 [&::-webkit-slider-thumb]:hover:bg-orange-600"
          @input="emitUpdate"
        />
      </div>

      <!-- Top K -->
      <div>
        <label class="label">
          <span class="label-text font-medium text-orange-900">Top K</span>
          <span class="label-text-alt text-orange-600">{{ localConfig.top_k }}</span>
        </label>
        <input 
          v-model.number="localConfig.top_k"
          type="range" 
          min="1" 
          max="100" 
          step="1"
          class="range bg-orange-100 [--range-shdw:theme(colors.orange.200)] hover:[--range-shdw:theme(colors.orange.300)] [&::-webkit-slider-thumb]:bg-orange-500 [&::-webkit-slider-thumb]:hover:bg-orange-600"
          @input="emitUpdate"
        />
      </div>

      <!-- Advanced Settings Toggle -->
      <div>
        <label class="cursor-pointer label">
          <span class="label-text text-orange-900">Show advanced settings</span>
          <input 
            v-model="showAdvanced" 
            type="checkbox" 
            class="checkbox border-orange-300 checked:border-orange-500 checked:bg-orange-500 hover:checked:bg-orange-600" 
          />
        </label>
      </div>

      <!-- Advanced Settings -->
      <div v-if="showAdvanced" class="space-y-4 border-t border-orange-200/50 pt-4">
        <!-- Frequency Penalty -->
        <div>
          <label class="label">
            <span class="label-text font-medium text-orange-900">Frequency Penalty</span>
            <span class="label-text-alt text-orange-600">{{ localConfig.frequency_penalty }}</span>
          </label>
          <input 
            v-model.number="localConfig.frequency_penalty"
            type="range" 
            min="-2" 
            max="2" 
            step="0.1"
            class="range bg-orange-100/70 [--range-shdw:theme(colors.orange.200)] hover:[--range-shdw:theme(colors.orange.300)] [&::-webkit-slider-thumb]:bg-orange-400 [&::-webkit-slider-thumb]:hover:bg-orange-500"
            @input="emitUpdate"
          />
        </div>

        <!-- Presence Penalty -->
        <div>
          <label class="label">
            <span class="label-text font-medium text-orange-900">Presence Penalty</span>
            <span class="label-text-alt text-orange-600">{{ localConfig.presence_penalty }}</span>
          </label>
          <input 
            v-model.number="localConfig.presence_penalty"
            type="range" 
            min="-2" 
            max="2" 
            step="0.1"
            class="range bg-orange-100/70 [--range-shdw:theme(colors.orange.200)] hover:[--range-shdw:theme(colors.orange.300)] [&::-webkit-slider-thumb]:bg-orange-400 [&::-webkit-slider-thumb]:hover:bg-orange-500"
            @input="emitUpdate"
          />
        </div>
      </div>

      <!-- Preset Buttons -->
      <div class="grid grid-cols-3 gap-2 pt-4 border-t border-orange-200/50">
        <button 
          @click="applyPreset('creative')" 
          class="btn btn-sm border-orange-200 hover:border-orange-300 bg-white/50 hover:bg-orange-50 text-orange-700 hover:text-orange-800 backdrop-blur-sm"
        >
          Creative
        </button>
        <button 
          @click="applyPreset('balanced')" 
          class="btn btn-sm border-orange-200 hover:border-orange-300 bg-white/50 hover:bg-orange-50 text-orange-700 hover:text-orange-800 backdrop-blur-sm"
        >
          Balanced
        </button>
        <button 
          @click="applyPreset('precise')" 
          class="btn btn-sm border-orange-200 hover:border-orange-300 bg-white/50 hover:bg-orange-50 text-orange-700 hover:text-orange-800 backdrop-blur-sm"
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
