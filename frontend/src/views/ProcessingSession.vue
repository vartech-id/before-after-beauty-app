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

// onMounted(async () => {
//   if (!filterCode.value || !state.photoPath) {
//     // kalau nggak ada data sesi, balikkan user
//     router.push({ name: "ProductSelections" });
//     return;
//   }

//   // contoh kirim ke FastAPI
//   await fetch("http://localhost:8000/api/apply-filter", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({
//       filter: filterCode.value, // 'MENCERAHKAN_KULIT', dll
//       photo_path: state.photoPath, // atau data lain yg kamu simpan
//     }),
//   });

//   router.push({ name: "ResultPage" });
// });

const goNext = () => router.push({ name: "ResultPage" });
</script>

<template>
  <h1>Processing Session</h1>
  <div class="processing">
    <img :src="loadingImage" alt="Loading..." />
    <p>Mohon tunggu, sedang memproses foto Anda...</p>
  </div>
  <button @click="goNext">Next</button>
</template>

<style scoped></style>
