<script setup>
import { onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";

const router = useRouter()

const handleHome = () => {
  router.push({ name: "WelcomeScreen" }); // balik ke awal
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const presetOptions = [
  { value: "cerah", label: "Mencerahkan Kulit (A)" },
  { value: "kerutan", label: "Mengurangi Keriput (B)" },
  { value: "lembab", label: "Melembabkan Kulit (C)" },
];

const controlDefs = [
  {
    key: "target_L",
    label: "Target Lightness (L*)",
    helper: "Semakin tinggi semakin cerah kulit keseluruhan.",
    min: 130,
    max: 190,
    step: 0.5,
  },
  {
    key: "max_delta_L",
    label: "Max Delta Lightness",
    helper: "Batas maksimal penambahan kecerahan dibanding kondisi awal.",
    min: 0,
    max: 30,
    step: 0.5,
  },
  {
    key: "smooth_strength",
    label: "Skin Smooth",
    helper: "Kekuatan perataan tekstur kulit utama.",
    min: 0,
    max: 1,
    step: 0.01,
  },
  {
    key: "eye_smooth_strength",
    label: "Under-Eye Smooth",
    helper: "Khusus area bawah mata agar kantung/garis halus tersamarkan.",
    min: 0,
    max: 1,
    step: 0.01,
  },
  {
    key: "glow_strength",
    label: "Soft Glow",
    helper: "Memberi efek glow lembut di area kulit.",
    min: 0,
    max: 0.4,
    step: 0.01,
  },
  {
    key: "saturation_boost",
    label: "Saturation Boost",
    helper: "Meningkatkan saturasi warna kulit & make-up.",
    min: 0.8,
    max: 1.3,
    step: 0.01,
  },
  {
    key: "hydration_highlight",
    label: "Hydration Highlight",
    helper: "Menambah highlight halus pada pipi agar tampak lembab.",
    min: 0,
    max: 0.6,
    step: 0.01,
  },
  {
    key: "wrinkle_soften",
    label: "Wrinkle Softening",
    helper: "Mengurangi kerutan/garis halus dengan blur selektif.",
    min: 0,
    max: 3,
    step: 0.05,
  },
  {
    key: "detail_mix",
    label: "Detail Mix",
    helper: "Mengembalikan detail kulit setelah smoothing (edge aware).",
    min: 0,
    max: 0.5,
    step: 0.01,
  },
  {
    key: "unsharp_amount",
    label: "Texture Sharpen Amount",
    helper: "Kekuatan unsharp mask untuk tekstur halus.",
    min: 0,
    max: 0.2,
    step: 0.005,
  },
  {
    key: "unsharp_radius",
    label: "Texture Sharpen Radius",
    helper: "Radius sharpening; lebih besar = area lebih lebar.",
    min: 0.5,
    max: 3,
    step: 0.05,
  },
  {
    key: "edge_enhance_mix",
    label: "Edge Enhance Mix",
    helper: "Seberapa banyak sharpening diterapkan di tepi wajah.",
    min: 0,
    max: 1,
    step: 0.02,
  },
];

const presets = ref({});
const selectedPreset = ref("cerah");

const config = reactive({
  target_L: 0,
  max_delta_L: 0,
  smooth_strength: 0,
  eye_smooth_strength: 0,
  glow_strength: 0,
  saturation_boost: 0,
  hydration_highlight: 0,
  wrinkle_soften: 0,
  detail_mix: 0,
  unsharp_amount: 0,
  unsharp_radius: 0,
  edge_enhance_mix: 0,
});

const selectedFile = ref(null);
const previewUrl = ref("");
const previewResultUrl = ref("");
const previewError = ref("");
const isPreviewing = ref(false);

const isSaving = ref(false);
const saveStatus = ref("");

let previewDebounce = null;
let previewAbort = null;

const setConfigFromPreset = (name) => {
  const base = presets.value?.[name];
  if (!base) return;
  Object.keys(config).forEach((key) => {
    if (typeof base[key] !== "undefined") {
      config[key] = base[key];
    }
  });
};

const loadPresets = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/presets`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    presets.value = data.presets || {};

    const initialPreset =
      presets.value[selectedPreset.value] !== undefined
        ? selectedPreset.value
        : Object.keys(presets.value)[0];
    if (initialPreset) {
      selectedPreset.value = initialPreset;
      setConfigFromPreset(initialPreset);
    }
  } catch (err) {
    previewError.value = `Gagal memuat preset: ${err.message || err}`;
  }
};

const onFileChange = (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  selectedFile.value = file;

  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = URL.createObjectURL(file);

  triggerPreview();
};

const triggerPreview = () => {
  if (!selectedFile.value) return;
  if (previewDebounce) clearTimeout(previewDebounce);
  previewDebounce = setTimeout(runPreview, 280);
};

const runPreview = async () => {
  if (!selectedFile.value) return;
  isPreviewing.value = true;
  previewError.value = "";

  if (previewAbort) {
    previewAbort.abort();
  }
  previewAbort = new AbortController();

  const formData = new FormData();
  formData.append("image", selectedFile.value);
  formData.append("preset", selectedPreset.value);
  formData.append("config", JSON.stringify({ ...config }));

  try {
    const res = await fetch(`${API_BASE}/api/presets/preview`, {
      method: "POST",
      body: formData,
      signal: previewAbort.signal,
    });

    if (!res.ok) {
      throw new Error(`Preview gagal (HTTP ${res.status})`);
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    if (previewResultUrl.value) URL.revokeObjectURL(previewResultUrl.value);
    previewResultUrl.value = url;
  } catch (err) {
    if (err.name !== "AbortError") {
      previewError.value = err.message || "Preview gagal dijalankan";
    }
  } finally {
    isPreviewing.value = false;
  }
};

const savePreset = async () => {
  isSaving.value = true;
  saveStatus.value = "Menyimpan ke preset utama...";
  try {
    const res = await fetch(
      `${API_BASE}/api/presets/${selectedPreset.value}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      }
    );
    if (!res.ok) {
      throw new Error(`Save gagal (HTTP ${res.status})`);
    }
    await loadPresets();
    saveStatus.value = "Tersimpan & langsung dipakai di main app.";
  } catch (err) {
    saveStatus.value = err.message || "Save gagal.";
  } finally {
    isSaving.value = false;
    setTimeout(() => {
      saveStatus.value = "";
    }, 2500);
  }
};

const resetPreset = () => {
  setConfigFromPreset(selectedPreset.value);
  triggerPreview();
  saveStatus.value = "Kembali ke nilai preset saat ini.";
  setTimeout(() => {
    saveStatus.value = "";
  }, 1500);
};

watch(selectedPreset, (val) => {
  setConfigFromPreset(val);
  triggerPreview();
});

onMounted(loadPresets);

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  if (previewResultUrl.value) URL.revokeObjectURL(previewResultUrl.value);
  if (previewAbort) previewAbort.abort();
});
</script>

<template>
  <div class="page-wrapper">
    <header class="hero">
      <div>
        <h1 class="app-title">Skin Setting Preview</h1>
        <p>
          Upload contoh foto, atur slider preset, lihat hasil real-time, lalu
          simpan supaya dipakai di alur utama.
        </p>
      </div>
      <div class="hero-actions">
        <label class="file-btn">
          <input type="file" accept="image/*" @change="onFileChange" />
          <span>Pilih Foto Sampel</span>
        </label>
        <div class="preset-select">
          <span class="preset">Preset yang disetel:</span>
          <select v-model="selectedPreset">
            <option
              v-for="option in presetOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>
        <div class="action-row">
          <button class="ghost-btn" @click="resetPreset">Reset ke Default</button>
          <button class="save-btn" :disabled="isSaving" @click="savePreset">
            {{ isSaving ? "Menyimpan..." : "Simpan ke Preset" }}
          </button>
          <button @click="handleHome">Home</button>
        </div>
        <span class="save-status" v-if="saveStatus">{{ saveStatus }}</span>
      </div>
    </header>

    <div class="preview-area">
      <div class="preview-card">
        <div class="preview-title">Foto Asli</div>
        <div class="preview-body">
          <img v-if="previewUrl" :src="previewUrl" alt="Original" />
          <p v-else class="empty">Upload foto untuk mulai preview.</p>
        </div>
      </div>
      <div class="preview-card">
        <div class="preview-title">
          Preview Hasil
          <span v-if="isPreviewing" class="chip">Rendering...</span>
        </div>
        <div class="preview-body">
          <img
            v-if="previewResultUrl"
            :src="previewResultUrl"
            alt="Preview result"
          />
          <p v-else class="empty">
            Atur slider setelah foto dipilih untuk melihat hasil.
          </p>
        </div>
        <p v-if="previewError" class="error">{{ previewError }}</p>
      </div>
    </div>

    <section class="controls">
      <div
        v-for="control in controlDefs"
        :key="control.key"
        class="control-row"
      >
        <div class="label-stack">
          <div class="label">{{ control.label }}</div>
          <div class="helper">{{ control.helper }}</div>
        </div>
        <div class="input-stack">
          <input
            type="range"
            :min="control.min"
            :max="control.max"
            :step="control.step"
            v-model.number="config[control.key]"
            @input="triggerPreview"
          />
          <input
            type="number"
            :min="control.min"
            :max="control.max"
            :step="control.step"
            v-model.number="config[control.key]"
            @input="triggerPreview"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24px 32px 48px;
  background: #000000;
  color: #e5e7eb;
  font-family: "Inter", system-ui, -apple-system, sans-serif;
}

.app-title{
    color: white;
}

.preset{
    color: white;
}

.hero {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(135deg, #0f172a, #0b1223);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.hero h1 {
  font-size: 26px;
  margin: 0 0 6px;
}

.hero p {
  margin: 0;
  color: #cbd5e1;
}

.hero-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.file-btn {
  background: #111827;
  border: 1px dashed #334155;
  color: #e2e8f0;
  padding: 10px 14px;
  border-radius: 12px;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.1s ease;
}

.file-btn:hover {
  border-color: #06b6d4;
  transform: translateY(-1px);
}

.file-btn input {
  display: none;
}

.preset-select {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 12px;
  border: 1px solid #1f2937;
  background: #0f172a;
}

.preset-select select {
  background: #0f172a;
  color: #e5e7eb;
  border: 1px solid #1f2937;
  border-radius: 10px;
  padding: 8px 10px;
  min-width: 220px;
}

.save-btn {
  background: linear-gradient(135deg, #06b6d4, #22d3ee);
  color: #0b1021;
  border: none;
  padding: 10px 16px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.2s ease;
}

.save-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(34, 211, 238, 0.2);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.save-status {
  color: #9ef0ff;
  font-size: 13px;
}

.ghost-btn {
  background: #111827;
  color: #e2e8f0;
  border: 1px solid #1f2937;
  padding: 10px 14px;
  border-radius: 12px;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.1s ease;
}

.ghost-btn:hover {
  border-color: #06b6d4;
  transform: translateY(-1px);
}

.action-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.preview-area {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.preview-card {
  border: 1px solid #1f2937;
  background: #0f172a;
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.preview-title {
  padding: 12px 14px;
  border-bottom: 1px solid #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e5e7eb;
  font-weight: 600;
}

.chip {
  background: #1e3a8a;
  color: #cbd5e1;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
}

.preview-body {
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
}

.preview-body img {
  max-height: 420px;
  width: 100%;
  object-fit: contain;
  border-radius: 10px;
  border: 1px solid #1f2937;
}

.empty {
  color: #94a3b8;
  text-align: center;
}

.error {
  color: #f87171;
  padding: 8px 12px 14px;
  margin: 0;
}

.controls {
  margin-top: 24px;
  border: 1px solid #1f2937;
  background: #0f172a;
  border-radius: 16px;
  padding: 18px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.control-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid #1f2937;
  border-radius: 12px;
  background: #0b1223;
}

.label-stack .label {
  font-weight: 600;
  color: #ffffff;
}

.helper {
  color: #94a3b8;
  font-size: 13px;
  margin-top: 2px;
}

.input-stack {
  display: grid;
  grid-template-columns: 1fr 110px;
  gap: 10px;
  align-items: center;
}

input[type="range"] {
  width: 100%;
  accent-color: #06b6d4;
  cursor: pointer;
}

input[type="number"] {
  width: 100%;
  background: #0f172a;
  border: 1px solid #1f2937;
  color: #e5e7eb;
  border-radius: 10px;
  padding: 8px 10px;
}

@media (max-width: 768px) {
  .hero-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .input-stack {
    grid-template-columns: 1fr;
  }
}

.page-wrapper{
    background-color: #000000;
    height: 100vh;
}
</style>
