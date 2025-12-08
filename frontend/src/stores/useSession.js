// src/stores/useSession.js
import { reactive, computed } from 'vue'

const state = reactive({
  selectedProduct: null,      // 'A' | 'B' | 'C'
  photoUrl: null,             // URL foto hasil capture (static/captured)
  photoPath: null,            // kalau mau simpan nama file hasil capture
  resultPhotoUrl: null,  // AFTER (hasil /api/beauty)
  resultAfterUrl: null,  // URL file tersimpan di backend/static/after
  resultFinalUrl: null,  // URL file tersimpan di backend/static/result
})

const filterCode = computed(() => {
  if (state.selectedProduct === 'A') return 'MENCERAHKAN_KULIT'
  if (state.selectedProduct === 'B') return 'MENGURANGI_KERIPUT'
  if (state.selectedProduct === 'C') return 'MELEMBABKAN_KULIT'
  return null
})


function clearSession() {
  state.selectedProduct = null
  state.photoUrl = null     // reset juga fotonya
  state.resultPhotoUrl = null
  state.resultAfterUrl = null
  state.resultFinalUrl = null
  
}

export function useSession() {
  // semua component yang import ini akan share state yang sama
  return {
    state,
    filterCode,
    clearSession,
  }
}
