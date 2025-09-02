import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import UploadView from '../views/UploadView.vue'
import TrainingView from '../views/TrainingView.vue'
import PredictionView from '../views/PredictionView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/upload',
    name: 'upload',
    component: UploadView
  },
  {
    path: '/train',
    name: 'train',
    component: TrainingView
  },
  {
    path: '/predict',
    name: 'predict',
    component: PredictionView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router