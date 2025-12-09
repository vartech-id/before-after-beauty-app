import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router' 
import VueKonva from "vue-konva"
import { preloadImages } from './utils/preloadImages.js'
import { logicOverlayUrls } from './constants/overlays.js'

// Warm up logic overlays globally so Result page renders instantly.
preloadImages(logicOverlayUrls)

createApp(App)
  .use(router)
  .use(VueKonva)
  .mount('#app')
