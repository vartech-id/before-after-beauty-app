<script setup>
import { useRouter } from "vue-router";
import { useSession } from "../stores/useSession";
import { computed } from "vue";
import { onMounted } from "vue";

const router = useRouter();
const { state, clearSession } = useSession();
const capturedPhotoUrl = computed(() => state.photoUrl);

onMounted(() => {
  // Safety: kalau belum pilih product atau belum capture foto, balikin
  if (!state.selectedProduct || !state.photoUrl) {
    router.push({ name: "PhotoSession" });
  }
});

const handleFinish = () => {
  clearSession(); // reset pilihan & data sesi
  router.push({ name: "WelcomeScreen" }); // balik ke awal
};
</script>

<template>
  <div class="resultPage">
    <div class=" resultWrapper">
      <img :src="state.photoUrl" alt="Before" />
      <img :src="state.resultPhotoUrl" alt="After" />
    </div>
    <div class="action-button">
      <button @click="">QR CODE</button>
      <button @click="handleFinish">Home</button>
    </div>
  </div>

</template>

<style scoped>
.resultPage{
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.resultWrapper {
  width: 100%;
  max-width: 900px;      /* atur di sini: 400 / 500 / 600 sesuai selera */
}
.resultWrapper img {
  width: 100%;           /* isi lebar container */
  height: auto;          /* jaga proporsi */
  display: block;
  margin-bottom: 8px;    /* jarak antar gambar */
  object-fit: cover;     /* atau "contain" kalau mau full terlihat */
}

.action-button{
  display: flex;
  flex-direction: row;
}

</style>
