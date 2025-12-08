<script setup>
import { useRouter } from "vue-router";
import { useSession } from "../stores/useSession";
import { computed, onMounted, ref } from "vue";

const router = useRouter();
const { state, clearSession } = useSession();

// Canvas mengikuti TemplateSetting.vue
const STORAGE_KEY = "template_4x6_v1";
const canvasWidthPx = 2400;
const canvasHeightPx = 3600;
const previewMaxWidth = 520; // ubah angka ini kalau preview terlalu besar/kecil

const defaultLayout = () => ({
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

const loadTemplateLayout = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;

    const parsed = JSON.parse(raw);
    const defaults = defaultLayout();

    templateLayout.value = {
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

onMounted(() => {
  // Safety: kalau belum pilih product atau belum capture foto, balikin
  if (!state.selectedProduct || !state.photoUrl) {
    router.push({ name: "PhotoSession" });
    return;
  }

  loadTemplateLayout();
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
          v-if="templateLayout.overlayEnabled && templateLayout.overlaySrc"
          :src="templateLayout.overlaySrc"
          class="overlayImage"
          :style="overlayStyle"
          alt="Overlay"
        />
      </div>
    </div>

    <div class="action-button">
      <button @click="">QR CODE</button>
      <button @click="handleFinish">Home</button>
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
  background: radial-gradient(circle at 20% 20%, #1f2937 0, #0b1020 55%);
  border: 1px solid #1f2937;
}

.overlayFrame {
  position: absolute;
  z-index: 4;
  border: 1px dashed rgba(148, 163, 184, 0.8);
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
}

</style>
