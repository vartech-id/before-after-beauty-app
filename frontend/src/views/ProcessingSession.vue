<script setup>
import { useRouter } from "vue-router";
import { computed, onMounted, ref } from "vue";
import { useSession } from "../stores/useSession";
import { preloadImages } from "../utils/preloadImages.js";

import loading_A from "./assets/LoadingAnimation/loading-a.webp";
import loading_B from "./assets/LoadingAnimation/loading-b.webp";
import loading_C from "./assets/LoadingAnimation/loading-c.webp";

const router = useRouter();
const { state, filterCode } = useSession();

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// ====== CONFIG: minimal waktu user lihat loading (ms) ======
const MS = 1000;
const MIN_LOADING_S = MS * 14; // ubah ke detik

// status
const processingDone = ref(false);
const minTimePassed = ref(false);

// URL foto hasil capture (BEFORE)
const capturedPhotoUrl = computed(() => state.photoUrl);

// mapping filterCode -> nama preset backend
const presetName = computed(() => {
  switch (filterCode.value) {
    case "MENCERAHKAN_KULIT":
      return "cerah";
    case "MELEMBABKAN_KULIT":
      return "lembab";
    case "MENGURANGI_KERIPUT":
      return "kerutan";
    default:
      return "cerah";
  }
});

// pilih image loading berdasarkan filter
const loadingImage = computed(() => {
  switch (filterCode.value) {
    case "MENCERAHKAN_KULIT":
      return loading_A;
    case "MENGURANGI_KERIPUT":
      return loading_B;
    case "MELEMBABKAN_KULIT":
      return loading_C;
    default:
      return "Error Animation";
  }
});

// helper: cek kapan boleh pindah ke ResultPage
const maybeGoNext = () => {
  if (processingDone.value && minTimePassed.value) {
    router.push({ name: "ResultPage" });
  }
};

onMounted(async () => {
  // Ensure the high-res loading animations are decoded before we show them.
  preloadImages([loading_A, loading_B, loading_C]);

  if (!state.photoUrl || !presetName.value) {
    router.push({ name: "PhotoSession" });
    return;
  }

  // ---- 1) timer minimal loading ----
  setTimeout(() => {
    minTimePassed.value = true;
    maybeGoNext();
  }, MIN_LOADING_S);

  // ---- 2) proses ke backend ----
  try {
    const imgRes = await fetch(state.photoUrl);
    const imgBlob = await imgRes.blob();

    const formData = new FormData();
    formData.append("image", imgBlob, "captured.jpg");
    formData.append("preset", presetName.value);

    const res = await fetch(`${API_BASE}/api/beauty`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      console.error("Beauty API error:", res.status);
      alert("Gagal memproses filter beauty");
      return;
    }

    // URL file tersimpan di backend (after/result)
    state.resultAfterUrl = res.headers.get("X-After-Url");
    state.resultFinalUrl = null; // final/composited akan diisi saat saveResultImage di ResultPage

    const outBlob = await res.blob();
    const outUrl = URL.createObjectURL(outBlob);

    state.resultPhotoUrl = outUrl;

    processingDone.value = true;
    maybeGoNext();
  } catch (err) {
    console.error("Error processing beauty:", err);
    alert("Terjadi error saat memproses foto.");
  }
});
</script>

<template>
  <div class="page">
    <div class="processing-wrapper">
    <div v-if="capturedPhotoUrl" class="photo-wrapper">
      <!-- Foto BEFORE -->
      <img :src="capturedPhotoUrl" alt="Captured photo" class="camera-image" />

      <!-- WEBP LOADING di atas foto -->
      <img
        :src="loadingImage"
        class="overlay-webp"
        loading="eager"
        fetchpriority="high"
        decoding="async"
      />
    </div>

    <p v-else>
      Tidak ada foto. Silakan kembali dan ambil foto terlebih dahulu.
    </p>
  </div>
  </div>

</template>

<style scoped>
  .page{
    height: 100vh;
    background: url(./assets/bg-last.png);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

.processing-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

/* wrapper foto jadi anchor untuk overlay */
.photo-wrapper {
  position: relative;
  width: 100%;
}

.photo {
  width: 100%;
  height: auto;
  display: block;
}

/* GIF full overlay di atas foto */
.overlay-webp {
  position: absolute;
  top: -636px;
  width: 100%;
  pointer-events: none;
}
</style>
