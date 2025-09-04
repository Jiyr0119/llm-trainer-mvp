// 导入Vue Router的核心函数
import { createRouter, createWebHistory } from 'vue-router'
// 导入各个页面组件
import HomeView from './views/HomeView.vue' // 首页
import UploadView from './views/UploadView.vue' // 数据上传页面
import DatasetsView from './views/DatasetsView.vue' // 数据集管理页面
import TrainingView from './views/TrainingView.vue' // 模型训练页面
import PredictionView from './views/PredictionView.vue' // 模型推理页面
import ErrorPage from './views/ErrorPage.vue' // 错误页面
import LoginView from './views/LoginView.vue' // 登录页面
import RegisterView from './views/RegisterView.vue' // 注册页面
import ProfileView from './views/ProfileView.vue' // 个人资料页面

// 定义路由配置数组
const routes = [
  {
    path: '/', // 路由路径
    name: 'home', // 路由名称，可用于编程式导航
    component: HomeView, // 对应的页面组件
    meta: { requiresAuth: false } // 不需要认证
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false } // 不需要认证
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false } // 不需要认证
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true } // 需要认证
  },
  {
    path: '/upload',
    name: 'upload',
    component: UploadView,
    meta: { requiresAuth: true } // 需要认证
  },
  {
    path: '/datasets',
    name: 'datasets',
    component: DatasetsView,
    meta: { requiresAuth: true } // 需要认证
  },
  {
    path: '/train',
    name: 'train',
    component: TrainingView,
    meta: { requiresAuth: true } // 需要认证
  },
  {
    path: '/predict',
    name: 'predict',
    component: PredictionView,
    meta: { requiresAuth: true } // 需要认证
  },
  {
    path: '/error/:type',
    name: 'error',
    component: ErrorPage,
    props: true,
    meta: { requiresAuth: false } // 不需要认证
  },
  {
    path: '/:pathMatch(.*)*', // 通配符路径，匹配所有未定义的路由
    name: 'not-found',
    redirect: '/error/404', // 重定向到404错误页面
    meta: { requiresAuth: false } // 不需要认证
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

// 导入认证服务
import authService from './services/auth'

// 全局前置守卫：在路由跳转前执行
router.beforeEach((to, from, next) => {
  // to: 即将进入的目标路由对象
  // from: 当前导航正要离开的路由对象
  // next: 函数，必须调用该方法来解析这个钩子
  
  // 检查路由是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  // 如果需要认证，检查用户是否已登录
  if (requiresAuth && !authService.isLoggedIn()) {
    // 未登录，重定向到登录页面，并传递原目标路由作为查询参数
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else {
    // 不需要认证或已登录，继续导航
    next()
  }
})

export default router