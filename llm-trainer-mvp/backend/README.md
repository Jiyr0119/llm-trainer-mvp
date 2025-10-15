# LLM Trainer 后端服务

基于 FastAPI 构建的大语言模型训练平台后端服务，提供数据集管理、模型训练、推理预测等核心功能的 RESTful API。

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLite (开发)/PostgreSQL (生产)
- **ORM**: SQLAlchemy + SQLModel
- **机器学习**: PyTorch, Transformers (Hugging Face)
- **认证**: JWT Token
- **测试**: Pytest
- **部署**: Uvicorn

## 目录结构

```
backend/
├── app/                    # 主应用目录
│   ├── api/               # API路由模块
│   │   ├── auth.py        # 认证相关接口
│   │   ├── datasets.py    # 数据集管理接口
│   │   ├── training.py    # 模型训练接口
│   │   ├── prediction.py  # 模型预测接口
│   │   ├── users.py       # 用户管理接口
│   │   └── chat.py        # 本地对话接口
│   ├── core/              # 核心模块
│   │   ├── config.py      # 配置管理
│   │   ├── middleware.py  # 中间件
│   │   ├── response.py    # 响应标准化
│   │   └── errors.py      # 错误处理
│   ├── services/          # 业务逻辑层
│   │   ├── dataset_service.py   # 数据集服务
│   │   ├── training_service.py  # 训练服务
│   │   └── prediction_service.py # 预测服务
│   ├── schemas/           # 数据模型(Pyndatic)
│   ├── models.py          # 数据库模型
│   └── db.py             # 数据库连接
├── data/                  # 数据存储目录
│   ├── uploads/          # 上传文件存储
│   ├── models/           # 模型文件存储
│   └── logs/             # 日志文件存储
├── scripts/               # 脚本工具
├── tests/                 # 测试文件
├── requirements.txt       # Python依赖
└── main.py               # 应用入口
```

## 功能模块

### 1. 认证与用户管理
- 用户注册、登录、登出
- JWT Token 认证机制
- 用户角色管理（普通用户/管理员）

### 2. 数据集管理
- CSV格式数据集上传
- 数据集列表查看
- 数据集预览与删除

### 3. 模型训练
- 基于BERT的文本分类模型训练
- 异步训练任务管理
- 训练进度监控
- 训练日志查看
- 训练任务停止

### 4. 模型预测
- 文本分类预测接口
- 模型缓存管理

### 5. 本地对话
- 本地语言模型对话功能

## 环境变量配置

项目使用 `.env` 文件进行配置管理，不同环境有不同的配置文件：

- `.env.dev` - 开发环境
- `.env.test` - 测试环境
- `.env.prod` - 生产环境

主要配置项包括：
- 数据库连接URL
- 文件存储路径
- 安全密钥
- 模型参数
- 日志配置

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行开发服务器

```bash
python main.py
```

默认运行在 `http://localhost:8001`

### 3. 运行测试

```bash
pytest
```

## API 文档

启动服务后，可通过以下地址访问自动生成的 API 文档：

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## 部署

推荐使用 Docker 进行部署，或者直接使用 Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

## 数据库迁移

项目支持从 SQLite 迁移到 PostgreSQL，相关脚本位于 `scripts/` 目录下。