<script setup>
import { useRouter } from "vue-router";
import { useSession } from "../stores/useSession";
import { computed } from "vue";
import { onMounted } from "vue";

const router = useRouter();
const { state,clearSession } = useSession();
const capturedPhotoUrl = computed(() => state.photoUrl)

onMounted(() => {
  // Safety: kalau belum pilih product atau belum capture foto, balikin
  if (!state.selectedProduct || !state.photoUrl) {
    router.push({ name: 'PhotoSession' })
  }

  // NANTI: di sini kamu bisa panggil FastAPI untuk apply filter
  // begitu selesai, router.push({ name: 'ResultPage' })
})


const handleFinish = () => {
  clearSession(); // reset pilihan & data sesi
  router.push({ name: "WelcomeScreen" }); // balik ke awal
};
</script>

<template>
  <h1>this is result page</h1>
  <img :src="state.photoUrl" alt="Before" />
  <img :src="state.resultPhotoUrl" alt="After" />
  <button @click="handleFinish">Home</button>
</template>

<style scoped>

</style>
