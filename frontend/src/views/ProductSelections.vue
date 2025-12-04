<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSession } from '../stores/useSession'

const router = useRouter()
const { state } = useSession()

// bridge ke data useSession.js
const selectedOption = computed({
  get: () => state.selectedProduct,
  set: (val) => (state.selectedProduct = val),
})


const goNext = () => {
    if(!selectedOption.value){
        alert('pilih salah satu!')
        return;
    }

    router.push({
        name: 'PhotoSession',
    })
}



</script>

<template>
  <h1>Product Selections</h1>
  <div class="cards-wrapper">
    <!-- Card A -->
    <label class="product-card" :class="{ active: selectedOption === 'A' }">
      <input
        type="radio"
        value="A"
        v-model="selectedOption"
        class="hidden-radio"
      />
      <img src="./assets/ULTIMATE-VIBRANT.png" alt="Mencerahkan Kulit" />
    </label>

    <!-- Card B -->
    <label class="product-card" :class="{ active: selectedOption === 'B' }">
      <input
        type="radio"
        value="B"
        v-model="selectedOption"
        class="hidden-radio"
      />
      <img src="./assets/ULTIMATE-RADIANCE.png" alt="Mencerahkan Kulit" />
    </label>

    <!-- Card C -->
    <label class="product-card" :class="{ active: selectedOption === 'C' }">
      <input
        type="radio"
        value="C"
        v-model="selectedOption"
        class="hidden-radio"
      />
      <img src="./assets/BIO-E.png" alt="Mencerahkan Kulit"/>
    </label>
  </div>

  <button @click="goNext">Next</button>
</template>

<style scoped>

.cards-wrapper{
    display: flex;
    flex-direction: row;
    width: 40%;
}

.hidden-radio {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.product-card {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-radius: 16px;
  padding: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card.active {
  transform: translateY(-4px) scale(1.03);
  box-shadow: 0 8px 16px rgba(0,0,0,.2);
}
</style>
