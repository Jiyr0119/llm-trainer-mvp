// 导入Vue核心库的createApp函数，用于创建Vue应用实例
import { createApp } from 'vue'
// 导入Element Plus组件库，提供UI组件
import ElementPlus from 'element-plus'
// 导入Element Plus的样式文件
import 'element-plus/dist/index.css'
// 导入根组件App
import App from './App.vue'
// 导入路由配置
import router from './router'
// 导入Pinia状态管理
import pinia from './store'

// 创建Vue应用实例
const app = createApp(App)
// 注册Element Plus插件，使其组件在整个应用中可用
app.use(ElementPlus)
// 注册路由插件，启用路由功能
app.use(router)
// 注册Pinia状态管理
app.use(pinia)
// 将应用挂载到DOM元素#app上，开始应用的生命周期
app.mount('#app')