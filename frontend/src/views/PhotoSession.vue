<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useSession } from "../stores/useSession";
import CameraCapture from "../components/CameraCapture.vue";

const router = useRouter();
const { state } = useSession();

const cameraRef = ref(null);

onMounted(() => {
  if (!state.selectedProduct) {
    router.push({ name: "ProductSelections" });
  }
});

const goNext = () => router.push({ name: "ProcessingSession" });
const goBack = () => router.push({ name: "ProductSelections" });

const handleCapture = () => {
  if (cameraRef.value) {
    cameraRef.value.takePhoto();
  }
};

const handleRetake = () => {
  if (cameraRef.value) {
    cameraRef.value.retakeCamera();
  }
};
</script>

<template>
  <div class="page">
    <div class="camera-wrapper">
      <CameraCapture ref="cameraRef" />

      <div class="camera-btn-wrapper">
        <!-- Button kiri -->
        <button
          class="btn"
          @click="state.photoUrl ? handleRetake() : goBack()"
        >
          {{ state.photoUrl ? "Retake" : "Back" }}
        </button>

        <!-- Button kanan -->
        <button
          class="btn"
          @click="state.photoUrl ? goNext() : handleCapture()"
        >
          {{ state.photoUrl ? "Next" : "Capture" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style>
.camera-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-top: 8em;
}

.camera-btn-wrapper {
  display: flex;
  gap: 5em; /* biar ada jarak */
  margin-top: 4em;
}

/* contoh styling tombol */
.btn {
  padding: 0.4em 1em;
  border-radius: 10px;
  font-size: 3em;
  background-color: #0096A9;
  color: white;
  font-weight: 700;
  font-family: 'Poppins', sans-serif;      
  letter-spacing: 2px;   
  border: none;                    
}
</style>
