<script setup>
import { useRouter } from "vue-router";
import { computed, onMounted } from "vue";
import { useSession } from "../stores/useSession";

// sesuaikan nama folder lengkapnya:
import loading_A from './assets/LoadingAnimation/loading-a.gif'
import loading_B from './assets/LoadingAnimation/loading-b.gif'
import loading_C from './assets/LoadingAnimation/loading-c.gif'

const router = useRouter();
const { state, filterCode } = useSession();

// URL foto hasil capture
const capturedPhotoUrl = computed(() => state.photoUrl)

// pilih image loading berdasarkan filter
const loadingImage = computed(() => {
  switch (filterCode.value) {
    case 'MENCERAHKAN_KULIT':
      return loading_A
    case 'MENGURANGI_KERIPUT':
      return loading_B
    case 'MELEMBABKAN_KULIT':
      return loading_C
    default:
      return loadingDefault
  }
})

onMounted(() => {
  // Safety: kalau belum pilih product atau belum capture foto, balikin
  if (!state.selectedProduct || !state.photoUrl) {
    router.push({ name: 'PhotoSession' })
  }

  // NANTI: di sini kamu bisa panggil FastAPI untuk apply filter
  // begitu selesai, router.push({ name: 'ResultPage' })
})

const handleNext = () => {
  router.push({name:'ResultPage'})
}
</script>

<template>
  <div class="processing-wrapper">
    <div v-if="capturedPhotoUrl" class="photo-wrapper">
      <img
        :src="capturedPhotoUrl"
        alt="Captured photo"
        class="photo"
      />
    </div>
    <p v-else>
      Tidak ada foto. Silakan kembali dan ambil foto terlebih dahulu.
    </p>
    <div class="loading-wrapper">
      <img
        :src="loadingImage"
        alt="Processing..."
        class="overlay-gif"
      />
    </div>
    <button @click="handleNext">
      next
    </button>
  </div>
</template>

<style scoped>
.processing-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.photo-wrapper {
  position: relative;
  max-width: 640px;
  width: 100%;
}

.photo {
  width: 100%;
  height: auto;
  display: block;
}

.overlay-gif {
  position: absolute;
  left: 20em;
  top: 0em;
  width: 30%;
  pointer-events: none;
}
</style>