<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const goNext = () => router.push({ name: 'ProductSelections' })
</script>

<template>
    <h1>Welcome Screen</h1>
<button @click="goNext">Touch to start</button>

</template>

<style scoped>

</style>
