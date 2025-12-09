<script setup>
import { ref, onBeforeUnmount } from "vue";

// simpen file yang dipilih
const selectedFile = ref(null);
// URL untuk preview
const previewUrl = ref(null);

// misal endpoint backend kamu
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const onFileChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;

  selectedFile.value = file;

  // kalau sudah pernah buat URL, revoke dulu biar gak bocor memory
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }

  // bikin URL sementara buat preview
  previewUrl.value = URL.createObjectURL(file);
};

const saveData = null
const brightness = ref(0);
const saturation = ref(0);
const hydration = ref(0);
const wrinkle_soften = ref(0);
const glowStrength = ref(10);
const value = ref(10);

onBeforeUnmount(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
});
</script>

<template>
  <div class="page">
    <div class="image-upload">
      <!-- input file -->
      <input type="file" accept="image/*" @change="onFileChange" />
      <!-- preview di atas -->
      <div v-if="previewUrl" class="preview-wrapper">
        <img :src="previewUrl" alt="Preview" class="preview-image" />
      </div>
    </div>
    <div class="filter-wrapper">
      <label for="skin-filter">Choose Your Filter:</label>
      <select id="skin-option" name="filter">
        <option value="A">MENCERAHKAN_KULIT</option>
        <option value="B">MENGURANGI_KERIPUT</option>
        <option value="C">MELEMBABKAN_KULIT</option>
      </select>
    </div>
  <div class="skin-adjustment-slider">
    <label for="brightness">brightness</label>
    <input
      type="range"
      v-model="brightness"
      min="0"
      max="100"
      step="1"
    />
    <input
      type="number"
      v-model.number="brightness"
      min="0"
      max="100"
    />
    <label for="brightness">brightness</label>
    <input
      type="range"
      v-model="brightness"
      min="0"
      max="100"
      step="1"
    />
    <input
      type="number"
      v-model.number="brightness"
      min="0"
      max="100"
    />
    <label for="brightness">brightness</label>
    <input
      type="range"
      v-model="brightness"
      min="0"
      max="100"
      step="1"
    />
    <input
      type="number"
      v-model.number="brightness"
      min="0"
      max="100"
    />
    <label for="brightness">brightness</label>
    <input
      type="range"
      v-model="brightness"
      min="0"
      max="100"
      step="1"
    />
    <input
      type="number"
      v-model.number="brightness"
      min="0"
      max="100"
    />

    <button @click="saveData">Save</button>
  </div>
  </div>
</template>

<style scoped>
.image-upload {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 500px;
}

.preview-wrapper {
  border: 1px solid #ccc;
  padding: 8px;
}

.preview-image {
  max-width: 100%;
  display: block;
}
</style>
