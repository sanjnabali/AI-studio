import { ref, nextTick } from 'vue'

export function useAutoResize(textareaRef: any) {
  const resize = () => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
      textareaRef.value.style.height = `${textareaRef.value.scrollHeight}px`
    }
  }

  const reset = () => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  }

  // Auto-resize on mount
  nextTick(() => {
    resize()
  })

  return {
    resize,
    reset
  }
}
