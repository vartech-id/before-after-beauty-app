<script setup>
import { useRouter } from "vue-router";
import { computed, onMounted, ref } from "vue";
import { useSession } from "../stores/useSession";

import loading_A from "./assets/LoadingAnimation/loading-a.gif";
import loading_B from "./assets/LoadingAnimation/loading-b.gif";
import loading_C from "./assets/LoadingAnimation/loading-c.gif";

import Overlay_Mencerahkan from "./assets/Overlay/overlay_mencerahkan.png"
import Overlay_Mengurangi_Keriput from "./assets/Overlay/overlay_keriput.png"
import Overlay_Melembabkan from "./assets/Overlay/overlay_melembabkan.png"

const router = useRouter();
const { state, filterCode } = useSession();

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// ====== CONFIG: minimal waktu user lihat loading (ms) ======
const MS = 1000;
const MIN_LOADING_S = MS * 13; // ubah ke detik

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

const imageOverlay = computed (() => {
    switch (filterCode.value) {
    case "MENCERAHKAN_KULIT":
      return Overlay_Mencerahkan;
    case "MENGURANGI_KERIPUT":
      return Overlay_Mengurangi_Keriput;
    case "MELEMBABKAN_KULIT":
      return Overlay_Melembabkan;
    default:
      return "Error Overlay";
  }
})

// helper: cek kapan boleh pindah ke ResultPage
const maybeGoNext = () => {
  if (processingDone.value && minTimePassed.value) {
    router.push({ name: "ResultPage" });
  }
};

onMounted(async () => {
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
    state.resultFinalUrl = res.headers.get("X-Result-Url") || state.resultAfterUrl;

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
  <div class="processing-wrapper">
    <div v-if="capturedPhotoUrl" class="photo-wrapper">
      <!-- Foto BEFORE -->
      <img :src="capturedPhotoUrl" alt="Captured photo" class="photo" />

      <!-- GIF LOADING di atas foto -->
      <img :src="loadingImage" alt="Processing..." class="overlay-gif" />
    </div>

    <p v-else>
      Tidak ada foto. Silakan kembali dan ambil foto terlebih dahulu.
    </p>
  </div>
</template>

<style scoped>
.processing-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

/* wrapper foto jadi anchor untuk overlay */
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

/* GIF full overlay di atas foto */
.overlay-gif {
  position: absolute;
  inset: 0;           /* top/right/bottom/left: 0 */
  width: 100%;
  height: 100%;
  object-fit: contain; /* atau 'cover' kalau mau nutup penuh */
  pointer-events: none;
}
</style>
