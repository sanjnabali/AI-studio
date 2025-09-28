import { ref } from 'vue'

export function useClipboard() {
  const copied = ref(false)

  const copy = async (text: string): Promise<boolean> => {
    try {
      await navigator.clipboard.writeText(text)
      copied.value = true
      setTimeout(() => {
        copied.value = false
      }, 2000)
      return true
    } catch (err) {
      console.error('Failed to copy text: ', err)
      copied.value = false
      return false
    }
  }

  return {
    copy,
    copied,
    isSupported: !!navigator.clipboard
  }
}
