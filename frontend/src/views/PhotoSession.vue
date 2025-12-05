<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useSession } from "../stores/useSession";
import CameraCapture from "../components/CameraCapture.vue";

const router = useRouter();
const { state } = useSession();

onMounted(() => {
  if (!state.selectedProduct) {
    // belum pilih produk, balikin ke ProductSelections
    router.push({ name: "ProductSelections" });
  }
});


const goNext = () => router.push({ name: "ProcessingSession" });
const goBack = () => router.push({ name: "ProductSelections" });
</script>

<template>
  <h1>Photo Session</h1>
  <CameraCapture />
  <button @click="goBack">Back</button>
      <button @click="goNext" :disabled="!state.photoUrl">
  Next
</button>
</template>

<style scoped></style>
