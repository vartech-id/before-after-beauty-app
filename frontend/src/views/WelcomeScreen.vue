<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
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
