<script setup>
import { useRouter } from "vue-router";
import { useSession } from "../stores/useSession";

const router = useRouter();
const { clearSession } = useSession();

const handleFinish = () => {
  clearSession(); // reset pilihan & data sesi
  router.push({ name: "WelcomeScreen" }); // balik ke awal
};
</script>

<template>
  <h1>this is result page</h1>
  <div class="result">
    <!-- tampilkan foto hasil, dll -->
    <button @click="handleFinish">Selesai / Mulai Sesi Baru</button>
  </div>
</template>

<style scoped></style>
