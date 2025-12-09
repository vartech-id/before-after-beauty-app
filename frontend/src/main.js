import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router' 
import VueKonva from "vue-konva"
import { preloadImages } from './utils/preloadImages.js'
import { logicOverlayUrls } from './constants/overlays.js'
import { staticAssetManifest } from './constants/preloadManifest.js'

// Warm up all static art and overlays so high-res assets are ready before navigation.
preloadImages([...logicOverlayUrls, ...staticAssetManifest])

createApp(App)
  .use(router)
  .use(VueKonva)
  .mount('#app')
