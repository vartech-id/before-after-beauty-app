// src/stores/useSession.js
import { reactive, computed } from 'vue'

const state = reactive({
  selectedProduct: null,      // 'A' | 'B' | 'C'
  photoPath: null,            // kalau mau simpan nama file hasil capture
  resultPhotoUrl: null,  // AFTER (hasil /api/beauty)
})

const filterCode = computed(() => {
  if (state.selectedProduct === 'A') return 'MENCERAHKAN_KULIT'
  if (state.selectedProduct === 'B') return 'MENGURANGI_KERIPUT'
  if (state.selectedProduct === 'C') return 'MELEMBABKAN_KULIT'
  return null
})

const presetName = computed(() => {
  switch (filterCode.value) {
    case 'MENCERAHKAN_KULIT':
      return 'cerah'     // 🔥 cocokin dengan PRESET_CONFIGS backend
    case 'MELEMBABKAN_KULIT':
      return 'lembab'
    case 'MENGURANGI_KERIPUT':
      return 'kerutan'
    default:
      return 'cerah'
  }
})

function clearSession() {
  state.selectedProduct = null
  state.photoUrl = null     // reset juga fotonya
  
}

export function useSession() {
  // semua component yang import ini akan share state yang sama
  return {
    state,
    filterCode,
    clearSession,
  }
}
