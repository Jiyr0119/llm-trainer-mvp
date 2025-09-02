# 大语言模型训练平台 MVP

这是一个可在本地运行的简化版大语言模型训练平台MVP，展示了核心功能流程。

## 功能特性

1. 数据集上传与管理
2. 基于BERT的文本分类模型训练
3. 模型推理演示
4. Web界面操作

## 环境要求

- Python 3.9+
- Node.js 16+
- 至少8GB内存

## 安装步骤

1. 克隆项目或复制代码到本地目录

2. 安装后端依赖：
```bash
cd backend
pip install -r requirements.txt
```

3. 安装前端依赖：
```bash
cd frontend
npm install
```

## 运行步骤

1. 启动后端服务：
```bash
cd backend
python main.py
```

2. 启动前端服务（新终端窗口）：
```bash
cd frontend
npm run dev
```

3. 打开浏览器访问：http://localhost:5173

## 使用说明

1. 首先在"数据上传"页面上传CSV格式的数据集（包含text和label列）
2. 在"模型训练"页面选择数据集并开始训练
3. 训练完成后，在"模型推理"页面测试模型效果

## 注意事项

- 此MVP版本仅用于演示核心功能流程
- 在生产环境中需要更多优化和安全措施
- 训练时间和资源消耗取决于数据集大小和硬件配置