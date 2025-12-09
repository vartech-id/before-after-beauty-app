<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useSession } from "../stores/useSession";

const router = useRouter();
const { state } = useSession();

// bridge ke data useSession.js
const selectedOption = computed({
  get: () => state.selectedProduct,
  set: (val) => (state.selectedProduct = val),
});

const goNext = () => {
  if (!selectedOption.value) {
    alert("pilih salah satu!");
    return;
  }

  router.push({
    name: "PhotoSession",
  });
};
</script>

<template>
  <div class="page">
    <div class="content-wrapper">
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

        <!-- Card C -->
        <label class="product-card" :class="{ active: selectedOption === 'C' }">
          <input
            type="radio"
            value="C"
            v-model="selectedOption"
            class="hidden-radio"
          />
          <img src="./assets/BIO-E.png" alt="Melembabkan Kulit" />
        </label>        

        <!-- Card B -->
        <label class="product-card product-card-garis-halus" :class="{ active: selectedOption === 'B' }">
          <input
            type="radio"
            value="B"
            v-model="selectedOption"
            class="hidden-radio"
          />
          <img src="./assets/ULTIMATE-RADIANCE.png" alt="Mengurangi Garis Halus" />
        </label>

      </div>
      <img class="next-btn" src="./assets/next.png" alt="next-button" @click="goNext" />
    </div>
  </div>
</template>

<style>
.content-wrapper{
  height: 100vh;
  display: flex;
  height: fit-content;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  gap: 20em;
  padding-top: 30em;

}

.cards-wrapper {
  display: flex;
  flex-direction: row;
  width: 80%;
  gap: 1em;
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
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  border: 2px solid transparent;   /* default: tidak kelihatan */
}

.product-card-garis-halus{
  padding-top: 1.1em;
}

.product-card.active {
  border-color: #0096A9;
  transform: translateY(-4px) scale(1.03);
  box-shadow: 0 8px 16px rgba(255, 255, 0, 0.3); /* optional glow */
}

.product-card.active {
  transform: translateY(-4px) scale(1.03);
  box-shadow: 0 8px 16px rgba(255, 0, 0, 0.2);
}

.next-btn {
  width: 80%;
}
</style>
