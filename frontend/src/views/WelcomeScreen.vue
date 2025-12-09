<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { preloadImages } from "../utils/preloadImages.js";

const router = useRouter();

const productSelectionAssets = [
  new URL("./assets/ULTIMATE-VIBRANT.png", import.meta.url).href,
  new URL("./assets/ULTIMATE-RADIANCE.png", import.meta.url).href,
  new URL("./assets/BIO-E.png", import.meta.url).href,
  new URL("./assets/next.png", import.meta.url).href,
];

onMounted(() => {
  // Warm up heavy images so the cards render instantly on navigation.
  preloadImages(productSelectionAssets);
});

const goNext = () => router.push({ name: "ProductSelections" });
</script>

<template>
  <div class="page">
        <img class="start-btn" src="./assets/start.png" alt="" @click="goNext">
  </div>
</template>

<style>
    .page{
    height: 100vh;
    background: url(./assets/bg.png);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    }
    .start-btn{
        width: 50%;
        height: fit-content;
        padding-top: 20em;
    }
</style>
