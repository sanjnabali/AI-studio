
<template>
  <div class="input-box">
    <h2>Multimodal Input</h2>

    <div class="input-group">
      <label for="textPrompt">Text Prompt:</label>
      <textarea id="textPrompt" v-model="textPrompt" placeholder="Enter your prompt..." />
      <button @click="submitText">Submit Text</button>
    </div>

    <div class="input-group">
      <label for="imageUpload">Upload Image:</label>
      <input id="imageUpload" type="file" accept="image/*" @change="onImageSelected" />
      <button :disabled="!selectedImage" @click="submitImage">Submit Image</button>
      <div v-if="imageResult">
        <strong>Image Label:</strong> {{ imageResult.label }} (Confidence: {{ (imageResult.confidence * 100).toFixed(1) }}%)
      </div>
    </div>

    <div class="input-group">
      <label for="audioUpload">Upload Audio (WAV):</label>
      <input id="audioUpload" type="file" accept="audio/wav" @change="onAudioSelected" />
      <button :disabled="!selectedAudio" @click="submitAudio">Submit Audio</button>
      <div v-if="audioResult">
        <strong>Transcription:</strong> {{ audioResult }}
      </div>
    </div>

    <div class="output-group" v-if="textResult">
      <h3>Text Completion Result</h3>
      <pre>{{ textResult }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const textPrompt = ref('')
const textResult = ref(null)
const selectedImage = ref(null)
const imageResult = ref(null)
const selectedAudio = ref(null)
const audioResult = ref(null)

// Backend base URL
const API_URL = 'http://localhost:8000'

const submitText = async () => {
  textResult.value = null
  try {
    const response = await axios.post(`${API_URL}/completion`, {
      prompt: textPrompt.value,
      max_new_tokens: 100,
      temperature: 0.7,
    })
    textResult.value = response.data.result
  } catch (err) {
    alert('Error during text completion: ' + err.message)
  }
}

const onImageSelected = (event) => {
  selectedImage.value = event.target.files[0]
  imageResult.value = null
}

const submitImage = async () => {
  if (!selectedImage.value) return
  const formData = new FormData()
  formData.append('file', selectedImage.value)

  try {
    const response = await axios.post(`${API_URL}/image2text/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    imageResult.value = response.data
  } catch (err) {
    alert('Error during image to text: ' + err.message)
  }
}

const onAudioSelected = (event) => {
  selectedAudio.value = event.target.files[0]
  audioResult.value = null
}

const submitAudio = async () => {
  if (!selectedAudio.value) return
  const formData = new FormData()
  formData.append('file', selectedAudio.value)

  try {
    const response = await axios.post(`${API_URL}/speech2text/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    audioResult.value = response.data.transcription
  } catch (err) {
    alert('Error during speech to text: ' + err.message)
  }
}
</script>

<style scoped>
.input-box {
  max-width: 600px;
  margin: 1rem auto;
  padding: 1rem;
  background: #f3f4f6;
  border-radius: 8px;
  font-family: Arial, sans-serif;
}
.input-group {
  margin-bottom: 1.5rem;
}
textarea {
  width: 100%;
  min-height: 80px;
  padding: 0.5rem;
  font-size: 1rem;
}
button {
  margin-top: 0.5rem;
}
.output-group pre {
  white-space: pre-wrap;
  background: white;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
}
</style>
