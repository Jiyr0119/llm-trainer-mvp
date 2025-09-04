// 导入Vue Router的核心函数
import { createRouter, createWebHistory } from 'vue-router'
// 导入各个页面组件
import LandingView from './views/LandingView.vue' // 登陆页面
import HomeView from './views/HomeView.vue' // 首页（登录后的主页）
import UploadView from './views/UploadView.vue' // 数据上传页面
import DatasetsView from './views/DatasetsView.vue' // 数据集管理页面
import TrainingView from './views/TrainingView.vue' // 模型训练页面
import PredictionView from './views/PredictionView.vue' // 模型推理页面
import ErrorPage from './views/ErrorPage.vue' // 错误页面
import LoginView from './views/LoginView.vue' // 登录页面
import RegisterView from './views/RegisterView.vue' // 注册页面
import ProfileView from './views/ProfileView.vue' // 个人资料页面
import ForgotPasswordView from './views/ForgotPasswordView.vue' // 忘记密码页面
import AdminView from './views/AdminView.vue' // 管理员控制面板页面

// 定义路由配置数组
const routes = [
  {
    path: '/', // 路由路径
    name: 'landing', // 路由名称，可用于编程式导航
    component: LandingView, // 对应的页面组件
    meta: { requiresAuth: false } // 不需要认证
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true } // 需要认证
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
    path: '/forgot-password',
    name: 'forgot-password',
    component: ForgotPasswordView,
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
    path: '/admin',
    name: 'admin',
    component: AdminView,
    meta: { requiresAuth: true, requiresAdmin: true } // 需要认证和管理员权限
  },
  {
    path: '/datasets',
    name: 'datasets',
    component: DatasetsView,
    meta: { requiresAuth: true, requiresAdmin: true } // 需要认证和管理员权限
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

// 导入Pinia存储
import { useAuthStore } from './store/auth'

// 全局前置守卫：在路由跳转前执行
router.beforeEach(async (to, from, next) => {
  // to: 即将进入的目标路由对象
  // from: 当前导航正要离开的路由对象
  // next: 函数，必须调用该方法来解析这个钩子
  
  // 获取认证存储
  const authStore = useAuthStore()
  
  // 检查路由是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  // 检查路由是否需要管理员权限
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  
  // 如果用户已登录，但访问的是登录、注册或忘记密码页面，重定向到主页
  if (authStore.isLoggedIn && (to.path === '/login' || to.path === '/register' || to.path === '/forgot-password' || to.path === '/')) {
    next({ path: '/home' })
    return
  }
  
  // 如果需要认证，检查用户是否已登录
  if (requiresAuth && !authStore.isLoggedIn) {
    // 未登录，重定向到登录页面，并传递原目标路由作为查询参数
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
    return
  }
  
  // 如果需要管理员权限，检查用户是否为管理员
  if (requiresAdmin) {
    // 如果用户信息不存在，先获取用户信息
    if (!authStore.currentUser) {
      try {
        await authStore.fetchUserInfo()
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 获取用户信息失败，可能是token过期，尝试刷新token
        try {
          await authStore.refreshToken()
          await authStore.fetchUserInfo()
        } catch (refreshError) {
          // 刷新token也失败，清除登录状态并重定向到登录页面
          console.error('刷新token失败:', refreshError)
          authStore.logout()
          next({
            path: '/login',
            query: { redirect: to.fullPath }
          })
          return
        }
      }
    }
    
    // 检查用户是否为管理员
    if (!authStore.isAdmin) {
      // 不是管理员，重定向到403错误页面
      next({ path: '/error/403' })
      return
    }
  }
  
  // 不需要认证或已登录且权限满足，继续导航
  next()
})

export default router