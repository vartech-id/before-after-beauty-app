<script setup>
import { useRouter } from "vue-router";
import { useSession } from "../stores/useSession";
import { computed, onMounted, ref } from "vue";
import Overlay_Mencerahkan from "./assets/Overlay/overlay_mencerahkan.png";
import Overlay_Mengurangi_Keriput from "./assets/Overlay/overlay_keriput.png";
import Overlay_Melembabkan from "./assets/Overlay/overlay_melembabkan.png";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const router = useRouter();
const { state, clearSession, filterCode } = useSession();

// Canvas mengikuti TemplateSetting.vue
const STORAGE_KEY = "template_4x6_v1";
const canvasWidthPx = 2400;
const canvasHeightPx = 3600;
const previewMaxWidth = 520;

const defaultLayout = () => ({
  overlayMode: "template",
  overlayEnabled: true,
  overlaySrc: null,
  overlayRel: { x: 0.05, y: 0.05, w: 0.9, h: 0.9 },
  photo1Rel: { x: 0.1, y: 0.14, w: 0.8, h: 0.3 },
  photo2Rel: { x: 0.1, y: 0.56, w: 0.8, h: 0.3 },
});

const templateLayout = ref(defaultLayout());

const canvasStyle = computed(() => ({
  maxWidth: `${previewMaxWidth}px`,
  aspectRatio: `${canvasWidthPx} / ${canvasHeightPx}`,
}));

const relToStyle = (rel) => ({
  left: `${rel.x * 100}%`,
  top: `${rel.y * 100}%`,
  width: `${rel.w * 100}%`,
  height: `${rel.h * 100}%`,
});

const overlayStyle = computed(() => relToStyle(templateLayout.value.overlayRel));
const beforeSlotStyle = computed(() => relToStyle(templateLayout.value.photo1Rel));
const afterSlotStyle = computed(() => relToStyle(templateLayout.value.photo2Rel));

const productOverlayMap = {
  MENCERAHKAN_KULIT: Overlay_Mencerahkan,
  MENGURANGI_KERIPUT: Overlay_Mengurangi_Keriput,
  MELEMBABKAN_KULIT: Overlay_Melembabkan,
};

const overlayImageSrc = computed(() => {
  if (!templateLayout.value.overlayEnabled) return null;
  if (templateLayout.value.overlayMode === "logic") {
    return productOverlayMap[filterCode.value] || null;
  }
  if (templateLayout.value.overlayMode === "template") {
    return templateLayout.value.overlaySrc || null;
  }
  return null;
});

const saveStatus = ref("");
const isSaving = ref(false);
const autoSaveCompleted = ref(false); // Flag untuk menandai auto save sudah selesai
const showQr = ref(false);
const qrLoading = ref(false);
const qrError = ref("");
const qrData = ref(null);

const loadTemplateLayout = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;

    const parsed = JSON.parse(raw);
    const defaults = defaultLayout();

    templateLayout.value = {
      overlayMode: parsed.overlayMode || defaults.overlayMode,
      overlayRel: { ...defaults.overlayRel, ...(parsed.overlayRel || {}) },
      photo1Rel: { ...defaults.photo1Rel, ...(parsed.photo1Rel || {}) },
      photo2Rel: { ...defaults.photo2Rel, ...(parsed.photo2Rel || {}) },
      overlayEnabled:
        typeof parsed.overlayEnabled === "boolean"
          ? parsed.overlayEnabled
          : defaults.overlayEnabled,
      overlaySrc: parsed.overlaySrc || defaults.overlaySrc,
    };
  } catch (err) {
    console.warn("Failed to load saved template, using defaults", err);
  }
};

const saveResultImage = async () => {
  if (!state.photoUrl || !state.resultAfterUrl) {
    alert("Foto before/after belum tersedia.");
    return false;
  }
  
  isSaving.value = true;
  saveStatus.value = "";
  try {
    const res = await fetch(`${API_BASE}/api/render-result`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        before_url: state.photoUrl,
        after_url: state.resultAfterUrl,
        overlay_enabled: templateLayout.value.overlayEnabled,
        overlay_mode: templateLayout.value.overlayMode,
        overlay_src:
          templateLayout.value.overlayMode === "template"
            ? templateLayout.value.overlaySrc
            : null,
        overlay_rel: templateLayout.value.overlayRel,
        photo1_rel: templateLayout.value.photo1Rel,
        photo2_rel: templateLayout.value.photo2Rel,
        filter_code: filterCode.value,
        canvas_width: canvasWidthPx,
        canvas_height: canvasHeightPx,
      }),
    });

    if (!res.ok) {
      throw new Error(`Save failed: ${res.status}`);
    }
    const data = await res.json();
    state.resultFinalUrl = data.result_url;
    saveStatus.value = "Auto-saved to result";
    autoSaveCompleted.value = true; // Tandai bahwa auto save selesai
    return true;
  } catch (err) {
    console.error("Save result error:", err);
    saveStatus.value = "Auto-save failed";
    return false;
  } finally {
    isSaving.value = false;
    setTimeout(() => {
      saveStatus.value = "";
    }, 2000);
  }
};

// Fungsi untuk manual save (jika masih diperlukan)
const manualSaveResultImage = async () => {
  const success = await saveResultImage();
  if (success) {
    saveStatus.value = "Manually saved to result";
  }
};

const openQrModal = async () => {
  if (!state.resultFinalUrl) {
    alert("Simpan hasil terlebih dahulu sebelum membuat QR.");
    return;
  }
  qrLoading.value = true;
  qrError.value = "";
  qrData.value = null;
  try {
    const res = await fetch(`${API_BASE}/api/drive/latest`);
    if (res.status === 404) {
      qrError.value = "Belum ada file terunggah ke Drive. Tunggu upload selesai.";
      return;
    }
    if (!res.ok) throw new Error(`Failed to fetch latest drive file: ${res.status}`);
    const data = await res.json();
    qrData.value = data;
    showQr.value = true;
  } catch (err) {
    console.error("QR modal error:", err);
    qrError.value = "Gagal memuat data QR.";
  } finally {
    qrLoading.value = false;
  }
};

const closeQrModal = () => {
  showQr.value = false;
};

onMounted(async () => {
  // Safety: kalau belum pilih product atau belum capture foto, balikin
  if (!state.selectedProduct || !state.photoUrl) {
    router.push({ name: "PhotoSession" });
    return;
  }

  loadTemplateLayout();
  
  // Auto save saat halaman dimuat
  await saveResultImage();
});

const handleFinish = () => {
  clearSession(); // reset pilihan & data sesi
  router.push({ name: "WelcomeScreen" }); // balik ke awal
};
</script>
<template>
  <div class="resultPage">
    <div class="resultWrapper">
      <div class="layoutCanvas" :style="canvasStyle">
        <div
          v-if="templateLayout.overlayEnabled"
          class="overlayFrame"
          :style="overlayStyle"
        ></div>

        <div class="slot beforeSlot" :style="beforeSlotStyle">
          <img v-if="state.photoUrl" :src="state.photoUrl" alt="Before" />
          <span class="slotLabel">Before</span>
        </div>

        <div class="slot afterSlot" :style="afterSlotStyle">
          <img
            v-if="state.resultPhotoUrl"
            :src="state.resultPhotoUrl"
            alt="After"
          />
          <span class="slotLabel">After</span>
        </div>

        <img
          v-if="overlayImageSrc"
          :src="overlayImageSrc"
          class="overlayImage"
          :style="overlayStyle"
          alt="Overlay"
        />
      </div>
    </div>
    
    <div class="status-indicator" v-if="isSaving || saveStatus || qrError || qrLoading">
      <span v-if="isSaving">⏳ Saving HD Result...</span>
      <span v-else-if="qrLoading">⏳ Uploading to Drive...</span>
      <span v-else-if="saveStatus" class="saveStatus">{{ saveStatus }}</span>
      <span v-else-if="qrError" class="saveStatus error">Drive: {{ qrError }}</span>
    </div>

    <div class="action-button">
      <!-- <button
        @click="manualSaveResultImage"
        :disabled="isSaving || autoSaveCompleted"
      >
        {{ isSaving ? "Saving..." : autoSaveCompleted ? "Saved" : "Save HD Result" }}
      </button> -->
      <button @click="openQrModal" :disabled="qrLoading || !state.resultFinalUrl">
        {{ qrLoading ? "Loading QR..." : "QR CODE" }}
      </button>
      <button @click="handleFinish">Home</button>
    </div>

    <div v-if="qrError" class="qr-error">{{ qrError }}</div>

    <div v-if="showQr && qrData" class="qr-modal">
      <div class="qr-dialog">
        <button class="close-btn" @click="closeQrModal">✕</button>
        <h3>Scan To Download</h3>
        <!-- <p class="file-name">{{ qrData.name }}</p>
        <a class="drive-link" :href="qrData.share_link" target="_blank">
          {{ qrData.share_link }}
        </a> -->
        <img :src="qrData.qr_url" alt="QR Code" class="qr-image" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.resultPage {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  padding: 24px 16px 40px;
}

.resultWrapper {
  width: 100%;
  display: flex;
  justify-content: center;
}

.layoutCanvas {
  position: relative;
  width: 100%;
  max-width: 100%;
  aspect-ratio: 2400 / 3600;
  overflow: hidden;
}

.overlayFrame {
  position: absolute;
  z-index: 4;
  border-radius: 10px;
  pointer-events: none;
  background: rgba(255, 255, 255, 0.02);
}

.overlayImage {
  position: absolute;
  z-index: 5;
  object-fit: fill;
  pointer-events: none;
}

.slot {
  position: absolute;
  overflow: hidden;
}

.slot img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.slotLabel {
  position: absolute;
  bottom: 8px;
  right: 8px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: rgba(17, 24, 39, 0.75);
  color: #e5e7eb;
}

.beforeSlot {
  z-index: 2;
}

.afterSlot {
  z-index: 3;
}

.action-button {
  display: flex;
  gap: 12px;
  justify-content: center;
  align-items: center;
}

.action-button button {
  padding: 10px 16px;
  border-radius: 10px;
  border: 1px solid #1f2937;
  background: #111827;
  color: #e5e7eb;
  cursor: pointer;
  transition: transform 120ms ease, box-shadow 120ms ease;
}

.action-button button:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.25);
}

.status-indicator {
  margin: 10px 0;
  padding: 8px 16px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  color: #3b82f6;
  font-size: 14px;
}

.status-indicator span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.saveStatus {
  font-size: 12px;
  color: #10b981; /* Hijau untuk sukses */
}

.saveStatus.error {
  color: #ef4444; /* Merah untuk error */
}

.qr-error {
  color: #ef4444;
  font-size: 13px;
}

.qr-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.qr-dialog {
  position: relative;
  background: #0f172a;
  border: 1px solid #1f2937;
  border-radius: 12px;
  padding: 20px;
  width: min(90%, 360px);
  color: #e5e7eb;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
  text-align: center;
}

.qr-dialog h3 {
  margin: 0 0 6px;
  font-size: 18px;
}

.qr-dialog .file-name {
  font-size: 14px;
  color: #cbd5e1;
  margin: 0 0 8px;
}

/* .qr-dialog .drive-link {
  display: inline-block;
  font-size: 13px;
  color: #60a5fa;
  word-break: break-all;
  margin-bottom: 12px;
} */

.qr-dialog .qr-image {
  width: 220px;
  height: 220px;
  margin: 0 auto;
  display: block;
  background: #fff;
  padding: 8px;
  border-radius: 8px;
}

.qr-dialog .close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #1f2937;
  border: 1px solid #334155;
  color: #e5e7eb;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  cursor: pointer;
}


</style>
