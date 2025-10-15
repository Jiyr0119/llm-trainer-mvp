# LLM Trainer 前端应用

基于 Vue 3 + Vite 构建的大语言模型训练平台前端应用，提供直观的用户界面来管理数据集、训练模型和进行预测。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **路由**: Vue Router
- **状态管理**: Pinia
- **UI组件库**: Element Plus
- **HTTP客户端**: Axios
- **测试**: Vitest + Vue Test Utils
- **样式**: CSS + Element Plus 样式系统

## 目录结构

```
frontend/
├── src/                    # 源代码目录
│   ├── components/        # 公共组件
│   ├── views/             # 页面组件
│   ├── services/          # API服务层
│   ├── store/             # 状态管理
│   ├── utils/             # 工具函数
│   ├── router.js          # 路由配置
│   ├── main.js            # 应用入口
│   └── config.js          # 应用配置
├── scripts/               # 脚本工具
├── public/                # 静态资源
├── tests/                 # 测试文件
├── package.json           # 项目依赖
├── vite.config.js         # Vite配置
└── index.html             # HTML模板
```

## 功能页面

### 1. 登录/注册
- 用户认证流程
- JWT Token 管理

### 2. 数据集管理
- 数据集上传 (CSV格式)
- 数据集列表查看
- 数据集预览与删除

### 3. 模型训练
- 训练参数配置
- 训练任务提交
- 训练进度监控
- 训练日志查看
- 训练任务停止

### 4. 模型预测
- 文本分类预测
- 预测结果展示

### 5. 本地对话
- 本地语言模型对话界面

### 6. 用户管理 (管理员)
- 用户列表查看
- 用户权限管理

## 环境配置

项目支持多种环境配置：

- `.env.development` - 开发环境
- `.env.test` - 测试环境
- `.env.production` - 生产环境

## 安装与运行

### 1. 安装依赖

```bash
npm install
```

### 2. 开发环境运行

```bash
npm run dev
```

默认运行在 `http://localhost:5173`

### 3. 构建生产版本

```bash
npm run build
```

### 4. 运行测试

```bash
# 运行单元测试
npm run test

# 运行测试并生成覆盖率报告
npm run test:coverage
```

## 代理配置

前端开发服务器配置了代理，将 `/api` 请求转发到后端服务：

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:8001', // 后端服务地址
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '/api')
  }
}
```

确保后端服务运行在 `http://localhost:8001`，或者修改代理配置中的目标地址。

## 代码规范

- 使用 Composition API 风格
- 组件命名采用 PascalCase
- 使用 Pinia 进行状态管理
- API 请求统一在 services 目录中管理
- 组件和页面分离，提高复用性

## 部署

构建后的静态文件可部署到任何支持静态文件托管的服务上，如：
- Nginx
- Apache
- Vercel
- Netlify
- GitHub Pages

部署时需要确保 API 代理配置正确，或者配置正确的 API 地址。