<!-- src/pages/TemplateSetting.vue -->
<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useSession } from "../stores/useSession";

const router = useRouter();
const {clearSession } = useSession();
/* ============================
   CANVAS: 4x6 VERTICAL @ 600dpi
   ============================ */
const HANDLE_SIZE = 14;
const canvasWidthPx = 2400; // 4 inch * 600 dpi
const canvasHeightPx = 3600; // 6 inch * 600 dpi
const dpi = 600;
const MIN_FRAME_WIDTH = 80; // minimal lebar slot (px di canvas real)
const MIN_FRAME_HEIGHT = 80; // minimal tinggi slot

// scaling preview biar muat di tengah
const maxPreviewWidth = 500;
const maxPreviewHeight = 700;

const previewScale = computed(() => {
  const sx = maxPreviewWidth / canvasWidthPx;
  const sy = maxPreviewHeight / canvasHeightPx;
  return Math.min(sx, sy, 1);
});

const stageConfig = computed(() => ({
  width: canvasWidthPx * previewScale.value,
  height: canvasHeightPx * previewScale.value,
}));

const bgRectConfig = computed(() => ({
  x: 0,
  y: 0,
  width: canvasWidthPx * previewScale.value,
  height: canvasHeightPx * previewScale.value,
  fill: "#ffffff",
  stroke: "#111827",
  strokeWidth: 2,
}));

/* ============================
   LOCAL STORAGE SAVE / LOAD
   ============================ */

const STORAGE_KEY = "template_4x6_v1";
const saveStatus = ref("");

function saveTemplate() {
  const payload = {
    overlayRel: overlayRel.value,
    photo1Rel: photo1Rel.value,
    photo2Rel: photo2Rel.value,
  };
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    saveStatus.value = "Saved";
    setTimeout(() => {
      saveStatus.value = "";
    }, 2000);
  } catch (err) {
    console.error("Failed to save template:", err);
    saveStatus.value = "Save failed";
    setTimeout(() => {
      saveStatus.value = "";
    }, 2000);
  }
}

onMounted(() => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const data = JSON.parse(raw);

    if (data.overlayRel) {
      overlayRel.value = { ...overlayRel.value, ...data.overlayRel };
    }
    if (data.photo1Rel) {
      photo1Rel.value = { ...photo1Rel.value, ...data.photo1Rel };
    }
    if (data.photo2Rel) {
      photo2Rel.value = { ...photo2Rel.value, ...data.photo2Rel };
    }
  } catch (err) {
    console.error("Failed to load template from storage:", err);
  }
});

/* ============================
   OVERLAY (FRAME)
   ============================ */

// pakai koordinat RELATIF biar ikut paper
const overlayRel = ref({
  x: 0.05,
  y: 0.05,
  w: 0.9,
  h: 0.9,
});

const overlayEnabled = ref(true);
const overlayImage = ref(null); // HTMLImageElement dari upload

function onOverlayFileChange(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  const img = new Image();
  img.onload = () => {
    overlayImage.value = img;
  };
  img.src = url;
}

const overlayImageConfig = computed(() => {
  if (!overlayImage.value) return null;
  const s = previewScale.value;
  const w = canvasWidthPx;
  const h = canvasHeightPx;
  return {
    image: overlayImage.value,
    x: overlayRel.value.x * w * s,
    y: overlayRel.value.y * h * s,
    width: overlayRel.value.w * w * s,
    height: overlayRel.value.h * h * s,
    draggable: overlayEnabled.value,
    listening: overlayEnabled.value,
  };
});

function onOverlayDragEnd(e) {
  const node = e.target;
  const s = previewScale.value;
  const w = canvasWidthPx;
  const h = canvasHeightPx;
  const realX = node.x() / s;
  const realY = node.y() / s;
  overlayRel.value.x = realX / w;
  overlayRel.value.y = realY / h;
}

// helper overlay form (px -> rel)
function setOverlayWidthPx(px) {
  overlayRel.value.w = Math.max(0, Math.min(1, px / canvasWidthPx));
}
function setOverlayHeightPx(px) {
  overlayRel.value.h = Math.max(0, Math.min(1, px / canvasHeightPx));
}
function setOverlayXFromPx(px) {
  overlayRel.value.x = px / canvasWidthPx;
}
function setOverlayYFromPx(px) {
  overlayRel.value.y = px / canvasHeightPx;
}

const overlayWidthPx = computed(() =>
  Math.round(overlayRel.value.w * canvasWidthPx)
);
const overlayHeightPx = computed(() =>
  Math.round(overlayRel.value.h * canvasHeightPx)
);
const overlayXpx = computed(() =>
  Math.round(overlayRel.value.x * canvasWidthPx)
);
const overlayYpx = computed(() =>
  Math.round(overlayRel.value.y * canvasHeightPx)
);

/* ============================
   TEMPLATE 1 (PHOTO 1 – atas)
   ============================ */

const photo1Rel = ref({
  x: 0.1,
  y: 0.14,
  w: 0.8,
  h: 0.3,
});

// image untuk template 1
const photo1Image = ref(null);

function onPhoto1FileChange(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  const img = new Image();
  img.onload = () => {
    photo1Image.value = img;
  };
  img.src = url;
}

const photo1RectConfig = computed(() => {
  const s = previewScale.value;
  const w = canvasWidthPx;
  const h = canvasHeightPx;
  return {
    x: photo1Rel.value.x * w * s,
    y: photo1Rel.value.y * h * s,
    width: photo1Rel.value.w * w * s,
    height: photo1Rel.value.h * h * s,
    stroke: "#ef4444",
    strokeWidth: 3,
    fill: "rgba(239, 68, 68, 0.25)",
    draggable: true,
  };
});

// 4 handle resize di sisi kanan, bawah, kiri, atas
const photo1HandlesConfig = computed(() => {
  const rect = photo1RectConfig.value;
  const hs = HANDLE_SIZE;

  const right = {
    x: rect.x + rect.width - hs / 2,
    y: rect.y + rect.height / 2 - hs / 2,
    width: hs,
    height: hs,
    fill: "#f97316",
    draggable: true,
  };

  const bottom = {
    x: rect.x + rect.width / 2 - hs / 2,
    y: rect.y + rect.height - hs / 2,
    width: hs,
    height: hs,
    fill: "#f97316",
    draggable: true,
  };

  const left = {
    x: rect.x - hs / 2,
    y: rect.y + rect.height / 2 - hs / 2,
    width: hs,
    height: hs,
    fill: "#f97316",
    draggable: true,
  };

  const top = {
    x: rect.x + rect.width / 2 - hs / 2,
    y: rect.y - hs / 2,
    width: hs,
    height: hs,
    fill: "#f97316",
    draggable: true,
  };

  return { right, bottom, left, top };
});

// config image yang mengikuti slot 1
const photo1ImageConfig = computed(() => {
  if (!photo1Image.value) return null;

  const rect = photo1RectConfig.value;
  const img = photo1Image.value;

  const imgW = img.width;
  const imgH = img.height;
  const frameW = rect.width;
  const frameH = rect.height;

  if (!imgW || !imgH || !frameW || !frameH) return null;

  const imgRatio = imgW / imgH;
  const frameRatio = frameW / frameH;

  let cropW, cropH, cropX, cropY;

  if (imgRatio > frameRatio) {
    // foto lebih lebar → crop kiri–kanan
    cropH = imgH;
    cropW = frameRatio * cropH;
    cropX = (imgW - cropW) / 2;
    cropY = 0;
  } else {
    // foto lebih tinggi / sama → crop atas–bawah
    cropW = imgW;
    cropH = cropW / frameRatio;
    cropX = 0;
    cropY = (imgH - cropH) / 2;
  }

  return {
    image: img,
    x: rect.x,
    y: rect.y,
    width: frameW,
    height: frameH,
    crop: {
      x: cropX,
      y: cropY,
      width: cropW,
      height: cropH,
    },
  };
});

// -----------------------
// Resize handle PHOTO 1
// -----------------------
const photo1RightHandleConfig = computed(() => {
  const rect = photo1RectConfig.value;
  return {
    x: rect.x + rect.width,
    y: rect.y + rect.height / 2,
    width: HANDLE_SIZE,
    height: HANDLE_SIZE,
    offsetX: HANDLE_SIZE / 2,
    offsetY: HANDLE_SIZE / 2,
    fill: "#0b1120",
    stroke: "#f97316",
    strokeWidth: 2,
    draggable: true,
    dragBoundFunc: (pos) => ({
      // hanya boleh geser horizontal
      x: pos.x,
      y: rect.y + rect.height / 2,
    }),
  };
});

const photo1BottomHandleConfig = computed(() => {
  const rect = photo1RectConfig.value;
  return {
    x: rect.x + rect.width / 2,
    y: rect.y + rect.height,
    width: HANDLE_SIZE,
    height: HANDLE_SIZE,
    offsetX: HANDLE_SIZE / 2,
    offsetY: HANDLE_SIZE / 2,
    fill: "#0b1120",
    stroke: "#f97316",
    strokeWidth: 2,
    draggable: true,
    dragBoundFunc: (pos) => ({
      // hanya boleh geser vertical
      x: rect.x + rect.width / 2,
      y: pos.y,
    }),
  };
});

function onPhoto1DragEnd(e) {
  const node = e.target;
  const s = previewScale.value;
  const w = canvasWidthPx;
  const h = canvasHeightPx;
  photo1Rel.value.x = node.x() / s / w;
  photo1Rel.value.y = node.y() / s / h;
}

function setPhoto1WidthPx(px) {
  photo1Rel.value.w = Math.max(0, Math.min(1, px / canvasWidthPx));
}
function setPhoto1HeightPx(px) {
  photo1Rel.value.h = Math.max(0, Math.min(1, px / canvasHeightPx));
}
function setPhoto1XFromPx(px) {
  photo1Rel.value.x = px / canvasWidthPx;
}
function setPhoto1YFromPx(px) {
  photo1Rel.value.y = px / canvasHeightPx;
}

// --- HANDLES RESIZE PHOTO 1 ---

function onPhoto1RightHandleDragMove(e) {
  const node = e.target;
  const s = previewScale.value;
  const hs = HANDLE_SIZE;

  const handleCenterXReal = (node.x() + hs / 2) / s; // koordinat di canvas real
  const rectXReal = photo1Rel.value.x * canvasWidthPx;

  let newWidthPx = handleCenterXReal - rectXReal;
  newWidthPx = Math.max(MIN_FRAME_WIDTH, newWidthPx);
  const maxWidthPx = canvasWidthPx - rectXReal;
  newWidthPx = Math.min(newWidthPx, maxWidthPx);

  setPhoto1WidthPx(newWidthPx);
}

function onPhoto1BottomHandleDragMove(e) {
  const node = e.target;
  const s = previewScale.value;
  const hs = HANDLE_SIZE;

  const handleCenterYReal = (node.y() + hs / 2) / s;
  const rectYReal = photo1Rel.value.y * canvasHeightPx;

  let newHeightPx = handleCenterYReal - rectYReal;
  newHeightPx = Math.max(MIN_FRAME_HEIGHT, newHeightPx);
  const maxHeightPx = canvasHeightPx - rectYReal;
  newHeightPx = Math.min(newHeightPx, maxHeightPx);

  setPhoto1HeightPx(newHeightPx);
}

function onPhoto1LeftHandleDragMove(e) {
  const node = e.target;
  const s = previewScale.value;
  const hs = HANDLE_SIZE;

  const handleCenterXReal = (node.x() + hs / 2) / s;
  const currentRightReal =
    (photo1Rel.value.x + photo1Rel.value.w) * canvasWidthPx;

  let newXReal = handleCenterXReal;
  // clamp supaya tidak melewati kanan dan tidak keluar canvas
  const maxXReal = currentRightReal - MIN_FRAME_WIDTH;
  newXReal = Math.min(newXReal, maxXReal);
  newXReal = Math.max(0, newXReal);

  const newWidthPx = currentRightReal - newXReal;

  photo1Rel.value.x = newXReal / canvasWidthPx;
  setPhoto1WidthPx(newWidthPx);
}

function onPhoto1TopHandleDragMove(e) {
  const node = e.target;
  const s = previewScale.value;
  const hs = HANDLE_SIZE;

  const handleCenterYReal = (node.y() + hs / 2) / s;
  const currentBottomReal =
    (photo1Rel.value.y + photo1Rel.value.h) * canvasHeightPx;

  let newYReal = handleCenterYReal;
  const maxYReal = currentBottomReal - MIN_FRAME_HEIGHT;
  newYReal = Math.min(newYReal, maxYReal);
  newYReal = Math.max(0, newYReal);

  const newHeightPx = currentBottomReal - newYReal;

  photo1Rel.value.y = newYReal / canvasHeightPx;
  setPhoto1HeightPx(newHeightPx);
}

const photo1WidthPx = computed(() =>
  Math.round(photo1Rel.value.w * canvasWidthPx)
);
const photo1HeightPx = computed(() =>
  Math.round(photo1Rel.value.h * canvasHeightPx)
);
const photo1Xpx = computed(() => Math.round(photo1Rel.value.x * canvasWidthPx));
const photo1Ypx = computed(() =>
  Math.round(photo1Rel.value.y * canvasHeightPx)
);

/* ============================
   TEMPLATE 2 (PHOTO 2 – bawah)
   ============================ */

const photo2Rel = ref({
  x: 0.1,
  y: 0.56,
  w: 0.8,
  h: 0.3,
});

// image untuk template 2
const photo2Image = ref(null);

function onPhoto2FileChange(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  const img = new Image();
  img.onload = () => {
    photo2Image.value = img;
  };
  img.src = url;
}

const photo2RectConfig = computed(() => {
  const s = previewScale.value;
  const w = canvasWidthPx;
  const h = canvasHeightPx;
  return {
    x: photo2Rel.value.x * w * s,
    y: photo2Rel.value.y * h * s,
    width: photo2Rel.value.w * w * s,
    height: photo2Rel.value.h * h * s,
    stroke: "#22c55e",
    strokeWidth: 3,
    fill: "rgba(34, 197, 94, 0.25)",
    draggable: true,
  };
});

// 4 handle resize untuk photo 2
const photo2HandlesConfig = computed(() => {
  const rect = photo2RectConfig.value;
  const hs = HANDLE_SIZE;

  const right = {
    x: rect.x + rect.width - hs / 2,
    y: rect.y + rect.height / 2 - hs / 2,
    width: hs,
    height: hs,
    fill: "#22c55e",
    draggable: true,
  };

  const bottom = {
    x: rect.x + rect.width / 2 - hs / 2,
    y: rect.y + rect.height - hs / 2,
    width: hs,
    height: hs,
    fill: "#22c55e",
    draggable: true,
  };

  const left = {
    x: rect.x - hs / 2,
    y: rect.y + rect.height / 2 - hs / 2,
    width: hs,
    height: hs,
    fill: "#22c55e",
    draggable: true,
  };

  const top = {
    x: rect.x + rect.width / 2 - hs / 2,
    y: rect.y - hs / 2,
    width: hs,
    height: hs,
    fill: "#22c55e",
    draggable: true,
  };

  return { right, bottom, left, top };
});

// config image yang mengikuti slot 2 (mode cover, fokus tengah)
const photo2ImageConfig = computed(() => {
  if (!photo2Image.value) return null;

  const rect = photo2RectConfig.value;
  const img = photo2Image.value;

  const imgW = img.width;
  const imgH = img.height;
  const frameW = rect.width;
  const frameH = rect.height;

  if (!imgW || !imgH || !frameW || !frameH) return null;

  const imgRatio = imgW / imgH;
  const frameRatio = frameW / frameH;

  let cropW, cropH, cropX, cropY;

  if (imgRatio > frameRatio) {
    // foto lebih lebar → crop kiri–kanan
    cropH = imgH;
    cropW = frameRatio * cropH;
    cropX = (imgW - cropW) / 2;
    cropY = 0;
  } else {
    // foto lebih tinggi / sama → crop atas–bawah
    cropW = imgW;
    cropH = cropW / frameRatio;
    cropX = 0;
    cropY = (imgH - cropH) / 2;
  }

  return {
    image: img,
    x: rect.x,
    y: rect.y,
    width: frameW,
    height: frameH,
    crop: {
      x: cropX,
      y: cropY,
      width: cropW,
      height: cropH,
    },
  };
});

// -----------------------
// Resize handle PHOTO 2
// -----------------------
const photo2RightHandleConfig = computed(() => {
  const rect = photo2RectConfig.value;
  return {
    x: rect.x + rect.width,
    y: rect.y + rect.height / 2,
    width: HANDLE_SIZE,
    height: HANDLE_SIZE,
    offsetX: HANDLE_SIZE / 2,
    offsetY: HANDLE_SIZE / 2,
    fill: "#0b1120",
    stroke: "#22c55e",
    strokeWidth: 2,
    draggable: true,
    dragBoundFunc: (pos) => ({
      x: pos.x,
      y: rect.y + rect.height / 2,
    }),
  };
});

const photo2BottomHandleConfig = computed(() => {
  const rect = photo2RectConfig.value;
  return {
    x: rect.x + rect.width / 2,
    y: rect.y + rect.height,
    width: HANDLE_SIZE,
    height: HANDLE_SIZE,
    offsetX: HANDLE_SIZE / 2,
    offsetY: HANDLE_SIZE / 2,
    fill: "#0b1120",
    stroke: "#22c55e",
    strokeWidth: 2,
    draggable: true,
    dragBoundFunc: (pos) => ({
      x: rect.x + rect.width / 2,
      y: pos.y,
    }),
  };
});

function onPhoto2DragEnd(e) {
  const node = e.target;
  const s = previewScale.value;
  const w = canvasWidthPx;
  const h = canvasHeightPx;
  photo2Rel.value.x = node.x() / s / w;
  photo2Rel.value.y = node.y() / s / h;
}

function setPhoto2WidthPx(px) {
  photo2Rel.value.w = Math.max(0, Math.min(1, px / canvasWidthPx));
}
function setPhoto2HeightPx(px) {
  photo2Rel.value.h = Math.max(0, Math.min(1, px / canvasHeightPx));
}
function setPhoto2XFromPx(px) {
  photo2Rel.value.x = px / canvasWidthPx;
}
function setPhoto2YFromPx(px) {
  photo2Rel.value.y = px / canvasHeightPx;
}

// --- HANDLES RESIZE PHOTO 2 ---

function onPhoto2RightHandleDragMove(e) {
  const node = e.target;
  const s = previewScale.value;
  const hs = HANDLE_SIZE;

  const handleCenterXReal = (node.x() + hs / 2) / s;
  const rectXReal = photo2Rel.value.x * canvasWidthPx;

  let newWidthPx = handleCenterXReal - rectXReal;
  newWidthPx = Math.max(MIN_FRAME_WIDTH, newWidthPx);
  const maxWidthPx = canvasWidthPx - rectXReal;
  newWidthPx = Math.min(newWidthPx, maxWidthPx);

  setPhoto2WidthPx(newWidthPx);
}

function onPhoto2BottomHandleDragMove(e) {
  const node = e.target;
  const s = previewScale.value;
  const hs = HANDLE_SIZE;

  const handleCenterYReal = (node.y() + hs / 2) / s;
  const rectYReal = photo2Rel.value.y * canvasHeightPx;

  let newHeightPx = handleCenterYReal - rectYReal;
  newHeightPx = Math.max(MIN_FRAME_HEIGHT, newHeightPx);
  const maxHeightPx = canvasHeightPx - rectYReal;
  newHeightPx = Math.min(newHeightPx, maxHeightPx);

  setPhoto2HeightPx(newHeightPx);
}

function onPhoto2LeftHandleDragMove(e) {
  const node = e.target;
  const s = previewScale.value;
  const hs = HANDLE_SIZE;

  const handleCenterXReal = (node.x() + hs / 2) / s;
  const currentRightReal =
    (photo2Rel.value.x + photo2Rel.value.w) * canvasWidthPx;

  let newXReal = handleCenterXReal;
  const maxXReal = currentRightReal - MIN_FRAME_WIDTH;
  newXReal = Math.min(newXReal, maxXReal);
  newXReal = Math.max(0, newXReal);

  const newWidthPx = currentRightReal - newXReal;

  photo2Rel.value.x = newXReal / canvasWidthPx;
  setPhoto2WidthPx(newWidthPx);
}

function onPhoto2TopHandleDragMove(e) {
  const node = e.target;
  const s = previewScale.value;
  const hs = HANDLE_SIZE;

  const handleCenterYReal = (node.y() + hs / 2) / s;
  const currentBottomReal =
    (photo2Rel.value.y + photo2Rel.value.h) * canvasHeightPx;

  let newYReal = handleCenterYReal;
  const maxYReal = currentBottomReal - MIN_FRAME_HEIGHT;
  newYReal = Math.min(newYReal, maxYReal);
  newYReal = Math.max(0, newYReal);

  const newHeightPx = currentBottomReal - newYReal;

  photo2Rel.value.y = newYReal / canvasHeightPx;
  setPhoto2HeightPx(newHeightPx);
}

const photo2WidthPx = computed(() =>
  Math.round(photo2Rel.value.w * canvasWidthPx)
);
const photo2HeightPx = computed(() =>
  Math.round(photo2Rel.value.h * canvasHeightPx)
);
const photo2Xpx = computed(() => Math.round(photo2Rel.value.x * canvasWidthPx));
const photo2Ypx = computed(() =>
  Math.round(photo2Rel.value.y * canvasHeightPx)
);

const handleHome = () => {
  clearSession(); // reset pilihan & data sesi
  router.push({ name: "WelcomeScreen" }); // balik ke awal
};

</script>

<template>
  <div class="template-page">
    <header class="template-header">
      <div class="header-top">
        <div>
          <h1>4x6 Print Template – Vertical</h1>
          <p class="subtitle">
            Canvas fixed 4x6 inch @ {{ dpi }} dpi → {{ canvasWidthPx }} ×
            {{ canvasHeightPx }} px. Atur Template 1 (atas), Template 2 (bawah),
            dan Overlay PNG.
          </p>
        </div>
        <div class="header-actions">
          <button class="save-btn" @click="saveTemplate">Save layout</button>
          <button class="home-btn" @click="handleHome">Home</button>
          <span v-if="saveStatus" class="save-status">
            {{ saveStatus }}
          </span>
        </div>
      </div>
    </header>

    <main class="template-layout">
      <!-- Kiri: info + upload overlay & foto -->
      <aside class="left-panel">
        <section class="form-section">
          <h2 class="section-title">Paper</h2>
          <div class="info-block">
            <div class="info-row">
              <span>Size:</span>
              <strong>4" x 6"</strong>
            </div>
            <div class="info-row">
              <span>Orientation:</span>
              <strong>Vertical</strong>
            </div>
            <div class="info-row">
              <span>DPI:</span>
              <strong>{{ dpi }}</strong>
            </div>
            <div class="info-row">
              <span>Canvas px:</span>
              <strong>{{ canvasWidthPx }} × {{ canvasHeightPx }}</strong>
            </div>
          </div>
        </section>

        <section class="form-section">
          <h2 class="section-title">Overlay Image</h2>

          <div class="form-group">
            <label for="overlay-file">Upload overlay (PNG/JPG)</label>
            <input
              id="overlay-file"
              type="file"
              accept="image/png,image/jpeg"
              @change="onOverlayFileChange"
            />
          </div>

          <label class="toggle">
            <input v-model="overlayEnabled" type="checkbox" />
            <span>Enable overlay</span>
          </label>

          <p class="hint">
            Setelah upload, overlay muncul di canvas (bisa drag). Ukuran &amp;
            posisi bisa diatur pakai input px di panel kanan.
          </p>
        </section>

        <section class="form-section">
          <h2 class="section-title">Preview Photos (opsional)</h2>

          <div class="form-group">
            <label for="photo1-file">Upload foto Template 1 (atas)</label>
            <input
              id="photo1-file"
              type="file"
              accept="image/png,image/jpeg"
              @change="onPhoto1FileChange"
            />
          </div>

          <div class="form-group">
            <label for="photo2-file">Upload foto Template 2 (bawah)</label>
            <input
              id="photo2-file"
              type="file"
              accept="image/png,image/jpeg"
              @change="onPhoto2FileChange"
            />
          </div>

          <p class="hint">
            Foto hanya untuk bantu layout, nanti waktu live bisa diganti dengan
            foto dari kamera.
          </p>
        </section>
      </aside>

      <!-- Tengah: preview canvas -->
      <section class="center-panel">
        <div class="canvas-card">
          <div class="canvas-header">
            <span>Print Layout Preview</span>
            <small>{{ canvasWidthPx }} × {{ canvasHeightPx }} px</small>
          </div>
          <div class="canvas-container">
            <v-stage :config="stageConfig">
              <v-layer>
                <!-- background kertas -->
                <v-rect :config="bgRectConfig" />
                <!-- foto 1 -->
                <v-image v-if="photo1ImageConfig" :config="photo1ImageConfig" />
                <!-- slot 1 -->
                <v-rect :config="photo1RectConfig" @dragend="onPhoto1DragEnd" />

                <!-- 4 resize handles photo 1 -->
                <v-rect
                  :config="photo1HandlesConfig.right"
                  @dragmove="onPhoto1RightHandleDragMove"
                />
                <v-rect
                  :config="photo1HandlesConfig.bottom"
                  @dragmove="onPhoto1BottomHandleDragMove"
                />
                <v-rect
                  :config="photo1HandlesConfig.left"
                  @dragmove="onPhoto1LeftHandleDragMove"
                />
                <v-rect
                  :config="photo1HandlesConfig.top"
                  @dragmove="onPhoto1TopHandleDragMove"
                />

                <v-text
                  :config="{
                    text: '1',
                    x: photo1RectConfig.x + photo1RectConfig.width / 2 - 10,
                    y: photo1RectConfig.y + photo1RectConfig.height / 2 - 18,
                    fontSize: 36,
                    fill: '#ffffff',
                    fontStyle: 'bold',
                  }"
                />

                <!-- resize handle slot 1 -->
                <v-rect
                  :config="photo1RightHandleConfig"
                  @dragmove="onPhoto1RightHandleDragMove"
                />
                <v-rect
                  :config="photo1BottomHandleConfig"
                  @dragmove="onPhoto1BottomHandleDragMove"
                />

                <!-- foto 2 -->
                <v-image v-if="photo2ImageConfig" :config="photo2ImageConfig" />
                <!-- slot 2 -->
                <v-rect :config="photo2RectConfig" @dragend="onPhoto2DragEnd" />

                <!-- 4 resize handles photo 2 -->
                <v-rect
                  :config="photo2HandlesConfig.right"
                  @dragmove="onPhoto2RightHandleDragMove"
                />
                <v-rect
                  :config="photo2HandlesConfig.bottom"
                  @dragmove="onPhoto2BottomHandleDragMove"
                />
                <v-rect
                  :config="photo2HandlesConfig.left"
                  @dragmove="onPhoto2LeftHandleDragMove"
                />
                <v-rect
                  :config="photo2HandlesConfig.top"
                  @dragmove="onPhoto2TopHandleDragMove"
                />

                <v-text
                  :config="{
                    text: '2',
                    x: photo2RectConfig.x + photo2RectConfig.width / 2 - 10,
                    y: photo2RectConfig.y + photo2RectConfig.height / 2 - 18,
                    fontSize: 36,
                    fill: '#ffffff',
                    fontStyle: 'bold',
                  }"
                />

                <!-- resize handle slot 2 -->
                <v-rect
                  :config="photo2RightHandleConfig"
                  @dragmove="onPhoto2RightHandleDragMove"
                />
                <v-rect
                  :config="photo2BottomHandleConfig"
                  @dragmove="onPhoto2BottomHandleDragMove"
                />

                <!-- overlay di paling atas -->
                <v-image
                  v-if="overlayImageConfig"
                  :config="overlayImageConfig"
                  @dragend="onOverlayDragEnd"
                />
              </v-layer>
            </v-stage>
          </div>
        </div>
      </section>

      <!-- Kanan: pengaturan template 1, template 2, overlay size/pos px -->
      <aside class="right-panel">
        <!-- TEMPLATE 1 -->
        <section class="form-section">
          <h2 class="section-title">Template 1 – Photo 1 (atas)</h2>

          <div class="form-row">
            <div class="form-group">
              <label for="p1-width">Width (px)</label>
              <input
                id="p1-width"
                type="number"
                :value="photo1WidthPx"
                @input="setPhoto1WidthPx(+$event.target.value)"
                min="10"
              />
            </div>
            <div class="form-group">
              <label for="p1-height">Height (px)</label>
              <input
                id="p1-height"
                type="number"
                :value="photo1HeightPx"
                @input="setPhoto1HeightPx(+$event.target.value)"
                min="10"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="p1-x">X (from left)</label>
              <input
                id="p1-x"
                type="number"
                :value="photo1Xpx"
                @input="setPhoto1XFromPx(+$event.target.value)"
              />
            </div>
            <div class="form-group">
              <label for="p1-y">Y (from top)</label>
              <input
                id="p1-y"
                type="number"
                :value="photo1Ypx"
                @input="setPhoto1YFromPx(+$event.target.value)"
              />
            </div>
          </div>
        </section>

        <!-- TEMPLATE 2 -->
        <section class="form-section">
          <h2 class="section-title">Template 2 – Photo 2 (bawah)</h2>

          <div class="form-row">
            <div class="form-group">
              <label for="p2-width">Width (px)</label>
              <input
                id="p2-width"
                type="number"
                :value="photo2WidthPx"
                @input="setPhoto2WidthPx(+$event.target.value)"
                min="10"
              />
            </div>
            <div class="form-group">
              <label for="p2-height">Height (px)</label>
              <input
                id="p2-height"
                type="number"
                :value="photo2HeightPx"
                @input="setPhoto2HeightPx(+$event.target.value)"
                min="10"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="p2-x">X (from left)</label>
              <input
                id="p2-x"
                type="number"
                :value="photo2Xpx"
                @input="setPhoto2XFromPx(+$event.target.value)"
              />
            </div>
            <div class="form-group">
              <label for="p2-y">Y (from top)</label>
              <input
                id="p2-y"
                type="number"
                :value="photo2Ypx"
                @input="setPhoto2YFromPx(+$event.target.value)"
              />
            </div>
          </div>
        </section>

        <!-- OVERLAY POS & SIZE -->
        <section class="form-section">
          <h2 class="section-title">Overlay Position & Size</h2>

          <div class="form-row">
            <div class="form-group">
              <label for="ov-width">Width (px)</label>
              <input
                id="ov-width"
                type="number"
                :value="overlayWidthPx"
                @input="setOverlayWidthPx(+$event.target.value)"
                min="10"
              />
            </div>
            <div class="form-group">
              <label for="ov-height">Height (px)</label>
              <input
                id="ov-height"
                type="number"
                :value="overlayHeightPx"
                @input="setOverlayHeightPx(+$event.target.value)"
                min="10"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="ov-x">X (from left)</label>
              <input
                id="ov-x"
                type="number"
                :value="overlayXpx"
                @input="setOverlayXFromPx(+$event.target.value)"
              />
            </div>
            <div class="form-group">
              <label for="ov-y">Y (from top)</label>
              <input
                id="ov-y"
                type="number"
                :value="overlayYpx"
                @input="setOverlayYFromPx(+$event.target.value)"
              />
            </div>
          </div>
        </section>
      </aside>
    </main>
  </div>
</template>

<style scoped>
.template-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #111827;
  color: #e5e7eb;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
}

.template-header {
  padding: 10px 16px;
  border-bottom: 1px solid #1f2937;
  background: #020617;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.template-header h1 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
}

.subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: #9ca3af;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.save-btn {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #22c55e;
  background: #16a34a;
  color: #ecfdf5;
  font-size: 12px;
  cursor: pointer;
}

.home-btn {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #22c55e;
  background: #003cff;
  color: #ecfdf5;
  font-size: 12px;
  cursor: pointer;
}

.save-btn:hover {
  background: #22c55e;
}

.save-status {
  font-size: 11px;
  color: #a5b4fc;
}

.template-layout {
  display: flex;
  flex: 1;
  min-height: 0;
}

/* LEFT PANEL */
.left-panel {
  width: 260px;
  padding: 12px;
  border-right: 1px solid #1f2937;
  background: #030712;
  box-sizing: border-box;
  overflow-y: auto;
}

/* CENTER PANEL */
.center-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  box-sizing: border-box;
}

.canvas-card {
  background: #020617;
  border-radius: 12px;
  border: 1px solid #1f2937;
  box-shadow: 0 18px 35px rgba(0, 0, 0, 0.8);
  padding: 10px;
  width: min(90%, 620px);
  box-sizing: border-box;
}

.canvas-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
  font-size: 12px;
  color: #9ca3af;
}

.canvas-header span {
  font-weight: 500;
  color: #e5e7eb;
}

.canvas-container {
  background: #0b1120;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* RIGHT PANEL */
.right-panel {
  width: 280px;
  padding: 12px;
  border-left: 1px solid #1f2937;
  background: #030712;
  box-sizing: border-box;
  overflow-y: auto;
}

/* FORMS */
.form-section {
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid #111827;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #9ca3af;
  margin: 0 0 8px 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}

label {
  font-size: 11px;
  margin-bottom: 3px;
  color: #9ca3af;
}

select,
input[type="number"],
input[type="text"],
input[type="file"] {
  font-size: 12px;
  padding: 6px 8px;
  border-radius: 4px;
  border: 1px solid #374151;
  outline: none;
  background: #020617;
  color: #e5e7eb;
}

input:focus,
select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.4);
}

.info-block {
  margin-top: 6px;
  padding: 6px 8px;
  border-radius: 6px;
  background: #020617;
  border: 1px solid #111827;
  font-size: 11px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row span {
  color: #9ca3af;
}

.info-row strong {
  color: #e5e7eb;
}

.form-row {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

.hint {
  font-size: 11px;
  color: #6b7280;
  margin: 0;
}

/* toggle */
.toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  margin-bottom: 8px;
}

.toggle input[type="checkbox"] {
  width: 14px;
  height: 14px;
}
</style>
