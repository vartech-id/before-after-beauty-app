import { createRouter, createWebHistory } from 'vue-router'
import WelcomeScreen from '../views/WelcomeScreen.vue'
import ProductSelections from '../views/ProductSelections.vue'
import PhotoSession from '../views/PhotoSession.vue'
import ProcessingSession from '../views/ProcessingSession.vue'
import ResultPage from '../views/ResultPage.vue'

const routes = [
  { path: '/', name: 'WelcomeScreen', component: WelcomeScreen },
  { path: '/product-selections', name: 'ProductSelections', component: ProductSelections },
  { path: '/photo-session', name: 'PhotoSession', component: PhotoSession },
  { path: '/processiong-session' , name: 'ProcessingSession', component: ProcessingSession},
  { path: '/result' , name: 'ResultPage', component: ResultPage}
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
