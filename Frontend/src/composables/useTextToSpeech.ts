import { ref } from 'vue'

export function useTextToSpeech() {
  const isSupported = ref('speechSynthesis' in window)
  const speaking = ref(false)

  const speak = async (text: string, options?: {
    voice?: SpeechSynthesisVoice
    rate?: number
    pitch?: number
    volume?: number
  }): Promise<void> => {
    if (!isSupported.value) {
      throw new Error('Text-to-speech not supported')
    }

    return new Promise((resolve, reject) => {
      const utterance = new SpeechSynthesisUtterance(text)

      if (options?.voice) utterance.voice = options.voice
      if (options?.rate) utterance.rate = options.rate
      if (options?.pitch) utterance.pitch = options.pitch
      if (options?.volume) utterance.volume = options.volume

      utterance.onstart = () => {
        speaking.value = true
      }

      utterance.onend = () => {
        speaking.value = false
        resolve()
      }

      utterance.onerror = (event) => {
        speaking.value = false
        reject(new Error(`Speech synthesis failed: ${event.error}`))
      }

      speechSynthesis.speak(utterance)
    })
  }

  const stop = () => {
    speechSynthesis.cancel()
    speaking.value = false
  }

  const pause = () => {
    speechSynthesis.pause()
  }

  const resume = () => {
    speechSynthesis.resume()
  }

  const getVoices = (): SpeechSynthesisVoice[] => {
    return speechSynthesis.getVoices()
  }

  return {
    speak,
    stop,
    pause,
    resume,
    getVoices,
    speaking,
    isSupported
  }
}
