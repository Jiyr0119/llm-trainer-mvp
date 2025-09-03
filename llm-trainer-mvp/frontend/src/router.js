// 导入Vue Router的核心函数
import { createRouter, createWebHistory } from 'vue-router'
// 导入各个页面组件
import HomeView from './views/HomeView.vue' // 首页
import UploadView from './views/UploadView.vue' // 数据上传页面
import DatasetsView from './views/DatasetsView.vue' // 数据集管理页面
import TrainingView from './views/TrainingView.vue' // 模型训练页面
import PredictionView from './views/PredictionView.vue' // 模型推理页面
import ErrorPage from './views/ErrorPage.vue' // 错误页面

// 定义路由配置数组
const routes = [
  {
    path: '/', // 路由路径
    name: 'home', // 路由名称，可用于编程式导航
    component: HomeView // 对应的页面组件
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
    path: '/error/:type',
    name: 'error',
    component: ErrorPage,
    props: true
  },
  {
    path: '/:pathMatch(.*)*', // 通配符路径，匹配所有未定义的路由
    name: 'not-found',
    redirect: '/error/404' // 重定向到404错误页面
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(), // 使用HTML5 History模式，创建干净的URL（没有#）
  routes, // 路由配置
  scrollBehavior() {
    // 控制页面切换时的滚动行为，这里设置为切换路由时滚动到页面顶部
    return { top: 0 }
  }
})

// 全局前置守卫：在路由跳转前执行
router.beforeEach((to, from, next) => {
  // to: 即将进入的目标路由对象
  // from: 当前导航正要离开的路由对象
  // next: 函数，必须调用该方法来解析这个钩子
  // 这里可以加入鉴权、权限验证或加载状态逻辑
  next() // 继续导航
})

export default router