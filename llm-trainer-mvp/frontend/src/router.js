import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import UploadView from './views/UploadView.vue'
import DatasetsView from './views/DatasetsView.vue'
import TrainingView from './views/TrainingView.vue'
import PredictionView from './views/PredictionView.vue'

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
    path: '/datasets',
    name: 'datasets',
    component: DatasetsView
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
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 简单路由守卫示例：可在需要时扩展鉴权
router.beforeEach((to, from, next) => {
  // 这里可以加入鉴权或加载状态逻辑
  next()
})

export default router