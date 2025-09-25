import { ref } from 'vue'

export function useVoice() {
  const isRecording = ref(false)
  const mediaRecorder = ref<MediaRecorder | null>(null)
  const audioChunks = ref<Blob[]>([])

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder.value = new MediaRecorder(stream)
      audioChunks.value = []

      mediaRecorder.value.ondataavailable = (event) => {
        audioChunks.value.push(event.data)
      }

      mediaRecorder.value.start()
      isRecording.value = true
    } catch (error) {
      console.error('Error starting recording:', error)
    }
  }

  function stopRecording(): Promise<Blob> {
    return new Promise((resolve) => {
      if (mediaRecorder.value && isRecording.value) {
        mediaRecorder.value.onstop = () => {
          const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
          resolve(audioBlob)
          isRecording.value = false
        }
        mediaRecorder.value.stop()
        mediaRecorder.value.stream.getTracks().forEach(track => track.stop())
      }
    })
  }

  return {
    isRecording,
    startRecording,
    stopRecording
  }
}