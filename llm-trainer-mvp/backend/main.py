# 导入必要的库和模块
# FastAPI相关导入
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query, Request  # FastAPI核心组件
from fastapi.middleware.cors import CORSMiddleware  # 跨域资源共享中间件
from fastapi.responses import FileResponse, JSONResponse  # 特殊响应类型
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

# 数据处理相关
import pandas as pd  # 数据分析库
import os  # 操作系统接口
import json  # JSON处理
import shutil  # 高级文件操作
import logging  # 日志记录
from datetime import datetime  # 日期时间处理
from typing import List, Optional, Dict  # 类型提示

# 数据库相关
from sqlmodel import Session, select  # SQLModel ORM

# 机器学习相关
from transformers import BertTokenizer, BertForSequenceClassification, AdamW  # Hugging Face Transformers
from torch.utils.data import Dataset, DataLoader  # PyTorch数据加载
import torch  # PyTorch深度学习框架
import time  # 时间测量
from pydantic import BaseModel  # 数据验证

# 本地模块导入
from app.models import DatasetORM, TrainingJobORM, ModelArtifactORM, get_session, init_db  # 数据库模型和会话管理
from app.core.middleware import setup_middleware  # 中间件设置
from app.core.response import APIResponse  # 统一响应工具
from app.core.errors import APIException, ErrorCode, ResourceNotFoundException, InvalidParamsException, DatasetNotFoundException, TrainingNotFoundException, ModelNotFoundException, DatabaseException, InternalServerException  # 异常和错误码
from app.core.logger import setup_logger, RequestIdContext  # 新的日志系统

# 配置日志系统
LOG_PATH = "../data/logs"  # 定义日志文件存储路径
os.makedirs(LOG_PATH, exist_ok=True)  # 确保日志目录存在

# 使用新的日志系统
logger = setup_logger(
    name="llm-trainer",
    log_file="../data/training.log",
    level=logging.INFO,
    request_id_context=RequestIdContext
)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(console_handler)

# 定义应用关键路径
UPLOAD_PATH = "../data/uploads"  # 上传文件存储路径
MODEL_PATH = "../data/models"  # 模型存储路径

# 确保必要的目录存在，不存在则创建
os.makedirs(UPLOAD_PATH, exist_ok=True)  # 创建上传目录
os.makedirs(MODEL_PATH, exist_ok=True)  # 创建模型目录

# 初始化FastAPI应用
app = FastAPI(title="LLM Trainer API")  # 创建应用实例

# 配置跨域资源共享(CORS)中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源访问，注意：生产环境应该限制为特定域名
    allow_credentials=True,  # 允许发送凭证
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# 设置自定义中间件（请求ID和异常处理）
setup_middleware(app)

# 添加全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    logger.error(f"请求验证错误: {exc}", extra={"request_path": request.url.path})
    return APIResponse.error(
        message="请求参数验证失败",
        code=ErrorCode.INVALID_PARAMS.value,
        data={"detail": exc.errors()},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    logger.error(f"HTTP异常: {exc.detail}", extra={"request_path": request.url.path})
    return APIResponse.error(
        message=str(exc.detail),
        code=exc.status_code,
        status_code=exc.status_code
    )

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """处理自定义API异常"""
    logger.error(f"API异常: {exc.message}", extra={
        "request_path": request.url.path,
        "error_code": exc.code,
        "error_data": exc.data
    })
    return APIResponse.error(
        message=exc.message,
        code=exc.code,
        data=exc.data,
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.exception(f"未捕获的异常: {str(exc)}", extra={"request_path": request.url.path})
    return APIResponse.error(
        message="服务器内部错误",
        code=ErrorCode.INTERNAL_SERVER_ERROR.value,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

# 添加异常处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    # 记录错误详情
    logger.error(f"请求验证错误: {str(exc)}", exc_info=True)
    
    # 提取错误详情
    error_details = []
    for error in exc.errors():
        error_details.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })
    
    # 返回格式化的错误响应
    return JSONResponse(
        status_code=400,
        content=APIResponse.error(
            message="请求参数验证失败",
            code=ErrorCode.INVALID_PARAMS.code,
            data=error_details
        )
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    # 记录错误详情
    logger.error(f"HTTP异常: {str(exc)}", exc_info=True)
    
    # 返回格式化的错误响应
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(
            message=exc.detail,
            code=exc.status_code,
            data=None
        )
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    # 记录错误详情
    logger.error(f"未捕获的异常: {str(exc)}", exc_info=True)
    
    # 返回格式化的错误响应
    return JSONResponse(
        status_code=500,
        content=APIResponse.error(
            message="服务器内部错误",
            code=ErrorCode.INTERNAL_SERVER_ERROR.code,
            data=None
        )
    )

# 初始化数据库连接和表结构
init_db()

# 创建模型缓存，用于存储已加载的模型，避免重复加载
model_cache = {}  # 模型缓存字典

# 使用新的APIResponse类替代旧的响应模型

# 数据模型定义
class DatasetInfo:
    """数据集信息类"""
    def __init__(self, id, name, file_path, created_at):
        self.id = id  # 数据集ID
        self.name = name  # 数据集名称
        self.file_path = file_path  # 文件路径
        self.created_at = created_at  # 创建时间

class TrainingRequest:
    """训练请求类"""
    def __init__(self, dataset_id: int, epochs: int = 3, learning_rate: float = 2e-5, batch_size: int = 16):
        self.dataset_id = dataset_id  # 数据集ID
        self.epochs = epochs  # 训练轮数
        self.learning_rate = learning_rate  # 学习率
        self.batch_size = batch_size  # 批次大小

class PredictionRequest(BaseModel):
    """预测请求模型"""
    text: str  # 要预测的文本
    model_id: Optional[int] = None  # 可选的模型ID，不提供则使用最新模型

class TrainingStatus(BaseModel):
    """训练状态响应模型"""
    status: str  # 任务状态（pending/running/completed/failed）
    message: str  # 状态消息
    job_id: Optional[int] = None  # 训练任务ID

# 自定义数据集类
class TextDataset(Dataset):
    """文本分类数据集类，用于将文本和标签转换为模型可用的张量格式"""
    def __init__(self, texts, labels, tokenizer, max_length=128):
        """初始化数据集
        
        Args:
            texts (List[str]): 文本列表
            labels (List[int]): 标签列表
            tokenizer: 分词器实例
            max_length (int): 文本最大长度，默认128
        """
        self.texts = texts  # 文本列表
        self.labels = labels  # 标签列表
        self.tokenizer = tokenizer  # 分词器
        self.max_length = max_length  # 最大序列长度
    
    def __len__(self):
        """返回数据集大小"""
        return len(self.texts)
    
    def __getitem__(self, idx):
        """获取指定索引的样本
        
        Args:
            idx (int): 样本索引
            
        Returns:
            dict: 包含input_ids, attention_mask和labels的字典
        """
        text = str(self.texts[idx])  # 获取文本并确保是字符串类型
        label = self.labels[idx]  # 获取标签
        
        # 使用tokenizer将文本转换为模型输入格式
        encoding = self.tokenizer(
            text,
            truncation=True,  # 截断超长文本
            padding='max_length',  # 填充到最大长度
            max_length=self.max_length,  # 最大长度
            return_tensors='pt'  # 返回PyTorch张量
        )
        
        # 返回模型所需的输入格式
        return {
            'input_ids': encoding['input_ids'].flatten(),  # 输入ID
            'attention_mask': encoding['attention_mask'].flatten(),  # 注意力掩码
            'labels': torch.tensor(label, dtype=torch.long)  # 标签
        }

# 加载模型和分词器
def load_model_and_tokenizer(model_path=None):
    """加载BERT模型和分词器
    
    Args:
        model_path (str, optional): 模型路径，如果为None则使用默认路径
        
    Returns:
        tuple: (model, tokenizer) 模型和分词器实例
        
    Raises:
        Exception: 加载模型失败时抛出异常
    """
    model_name = 'bert-base-chinese'
    try:
        # 尝试从本地加载模型
        local_model_path = model_path or os.path.join(MODEL_PATH, model_name)
        if os.path.exists(local_model_path):
            logger.info(f"从本地加载模型: {local_model_path}")
            tokenizer = BertTokenizer.from_pretrained(local_model_path)
            model = BertForSequenceClassification.from_pretrained(local_model_path, num_labels=2)
        else:
            # 从Hugging Face下载模型
            logger.info(f"从Hugging Face下载模型: {model_name}")
            tokenizer = BertTokenizer.from_pretrained(model_name)
            model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)
            
            # 保存到本地
            os.makedirs(local_model_path, exist_ok=True)
            tokenizer.save_pretrained(local_model_path)
            model.save_pretrained(local_model_path)
            logger.info(f"模型已保存到本地: {local_model_path}")
            
        return model, tokenizer
    except Exception as e:
        logger.error(f"加载模型失败: {str(e)}")
        raise Exception(f"无法加载 '{model_name}' 的分词器。如果您尝试从 `https://huggingface.co/models` 加载，请确保本地不存在同名目录。否则，请确认 '{model_name}' 是正确的路径，且该目录包含 BertTokenizer 分词器所需的所有相关文件。")

# 获取模型（带缓存）
def get_model(model_id=None):
    """获取模型，支持从缓存或数据库加载模型
    
    Args:
        model_id (int, optional): 模型ID。如果为None，则加载最新的训练模型或默认模型。
        
    Returns:
        tuple: (model, tokenizer) 模型和分词器实例
        
    Raises:
        Exception: 模型不存在或加载失败时抛出异常
    """
    # 如果指定了model_id，尝试加载特定模型
    if model_id:
        # 检查缓存
        if model_id in model_cache:
            logger.info(f"从缓存加载模型 ID: {model_id}")
            return model_cache[model_id]
        
        # 从数据库获取模型信息
        with get_session() as session:
            model_artifact = session.get(ModelArtifactORM, model_id)
            if not model_artifact:
                raise Exception(f"模型ID {model_id} 不存在")
            
            # 检查模型文件是否存在
            if not os.path.exists(model_artifact.model_path):
                raise Exception(f"模型文件不存在: {model_artifact.model_path}")
            
            # 加载模型
            model, tokenizer = load_model_and_tokenizer(model_artifact.model_path)
            model_cache[model_id] = (model, tokenizer)
            return model, tokenizer
    
    # 如果没有指定model_id，加载最新的模型
    with get_session() as session:
        # 查询最新的成功训练的模型
        statement = select(ModelArtifactORM).order_by(ModelArtifactORM.id.desc()).limit(1)
        result = session.exec(statement).first()
        
        if not result:
            # 如果没有训练好的模型，加载默认模型
            logger.info("没有找到训练好的模型，加载默认模型")
            model, tokenizer = load_model_and_tokenizer()
            return model, tokenizer
        
        # 检查缓存
        if result.id in model_cache:
            logger.info(f"从缓存加载最新模型 ID: {result.id}")
            return model_cache[result.id]
        
        # 加载模型
        logger.info(f"加载最新模型 ID: {result.id}, 路径: {result.model_path}")
        model, tokenizer = load_model_and_tokenizer(result.model_path)
        model_cache[result.id] = (model, tokenizer)
        return model, tokenizer

# API路由
@app.get("/", response_model=APIResponse)
async def root():
    return APIResponse(code=200, message="成功", data={"message": "LLM Trainer MVP API"})

# 推理接口
@app.post("/api/predict")
async def predict(request: PredictionRequest):
    start_time = time.time()
    try:
        # 参数验证
        if not request.text or len(request.text.strip()) == 0:
            return APIResponse.error("请提供有效的文本")
        
        # 加载模型和分词器
        try:
            model, tokenizer = get_model(request.model_id)
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            return APIResponse.error(f"加载模型失败: {str(e)}")
        
        # 设置为评估模式
        model.eval()
        
        # 对输入文本进行编码
        inputs = tokenizer(
            request.text,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )
        
        # 执行推理
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
        
        # 构建响应
        class_names = ["负面", "正面"]
        result = {
            "text": request.text,
            "predicted_class": class_names[predicted_class],
            "confidence": confidence,
            "processing_time": time.time() - start_time
        }
        
        return APIResponse.success(result, "预测成功")
    except Exception as e:
        logger.error(f"预测失败: {str(e)}")
        return APIResponse.error(f"预测失败: {str(e)}")

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        # 检查文件类型
        if not file.filename.endswith('.csv'):
            raise InvalidParamsException("只支持CSV文件格式")
            
        # 保存文件
        file_path = f"../data/uploads/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 验证CSV格式
        try:
            df = pd.read_csv(file_path)
            if 'text' not in df.columns or 'label' not in df.columns:
                os.remove(file_path)  # 删除不符合要求的文件
                raise InvalidParamsException("CSV文件必须包含'text'和'label'列")
        except Exception as e:
            os.remove(file_path)  # 删除无法解析的文件
            raise InvalidParamsException(f"CSV文件解析失败: {str(e)}")
        
        # 保存到数据库（ORM）
        try:
            with get_session() as session:
                ds = DatasetORM(name=file.filename, file_path=file_path)
                session.add(ds)
                session.flush()  # 获取自增ID
                dataset_id = ds.id
                session.commit()
        except Exception as e:
            os.remove(file_path)  # 删除文件，因为数据库操作失败
            raise DatabaseException(f"保存数据集信息失败: {str(e)}")
        
        return APIResponse.success(
            message="数据集上传成功",
            data={
                "id": dataset_id,
                "filename": file.filename
            }
        )
    except (InvalidParamsException, DatabaseException) as e:
        # 这些异常已经在上面抛出
        logger.error(f"数据集上传失败: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"数据集上传失败: {str(e)}", exc_info=True)
        raise InternalServerException(message="数据集上传失败")

@app.get("/datasets")
async def list_datasets():
    try:
        with get_session() as session:
            results = session.exec(select(DatasetORM)).all()
            datasets = [
                {"id": d.id, "name": d.name, "file_path": d.file_path, "created_at": d.created_at.isoformat()}
                for d in results
            ]
            return APIResponse.success(
                data={"datasets": datasets},
                message="获取数据集列表成功"
            )
    except Exception as e:
        logger.error(f"获取数据集列表失败: {str(e)}", exc_info=True)
        raise DatabaseException(message="获取数据集列表失败")

@app.post("/train")
async def start_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    try:
        # 获取数据集信息
        with get_session() as session:
            ds = session.get(DatasetORM, request.dataset_id)
            if not ds:
                raise DatasetNotFoundException("数据集未找到")
            file_path = ds.file_path
        
        # 创建训练任务记录
        with get_session() as session:
            job = TrainingJobORM(
                dataset_id=request.dataset_id,
                status='pending',
                model_name="",  # 将在训练完成后更新
                epochs=request.epochs,
                learning_rate=request.learning_rate,
                batch_size=request.batch_size,
                started_at=datetime.utcnow()
            )
            session.add(job)
            session.flush()  # 获取自增ID
            job_id = job.id
        
        # 启动后台训练任务
        background_tasks.add_task(
            train_model_task,
            job_id=job_id,
            dataset_id=request.dataset_id,
            epochs=request.epochs,
            learning_rate=request.learning_rate,
            batch_size=request.batch_size
        )
        
        return APIResponse.success(
            message="训练任务已提交",
            data={
                "status": "pending",
                "job_id": job_id
            }
        )
    except DatasetNotFoundException as e:
        logger.error(f"训练失败: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"训练失败: {str(e)}", exc_info=True)
        raise InternalServerException(message=f"训练失败: {str(e)}")

@app.get("/train/status")
async def get_training_status():
    try:
        with get_session() as session:
            # 获取最近的训练任务
            job = session.exec(select(TrainingJobORM).order_by(TrainingJobORM.id.desc()).limit(1)).first()
            
            if not job:
                return APIResponse.success(
                    message="没有训练记录",
                    data={"status": "ready", "job_id": None}
                )
            
            return APIResponse.success(
                message=f"训练状态: {job.status}",
                data={
                    "status": job.status,
                    "job_id": job.id,
                    "progress": job.progress if hasattr(job, 'progress') else 0
                }
            )
    except Exception as e:
        logger.error(f"获取训练状态失败: {str(e)}", exc_info=True)
        raise InternalServerException(message="获取训练状态失败")

@app.post("/train/stop", response_model=APIResponse)
async def stop_training(request: dict):
    try:
        job_id = request.get("job_id")
        if not job_id:
            return APIResponse(
                code=400,
                message="缺少job_id参数",
                data=None
            )
            
        with get_session() as session:
            job = session.get(TrainingJobORM, job_id)
            if not job:
                return APIResponse(
                    code=404,
                    message="训练任务未找到",
                    data=None
                )
            
            # 如果任务已经完成，则返回相应状态
            if job.status == 'completed':
                return APIResponse(
                    code=200,
                    message="训练已完成，无需停止",
                    data={"status": "completed"}
                )
            
            # 更新任务状态为已停止
            job.status = 'stopped'
            job.completed_at = datetime.utcnow()
            session.add(job)
            
            return APIResponse(
                code=200,
                message="训练已停止",
                data={"status": "stopped"}
            )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"停止训练失败: {str(e)}",
            data=None
        )

@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        # 加载模型和分词器
        try:
            model, tokenizer = get_model(request.model_id)
        except Exception as e:
            raise ModelNotFoundException(f"加载模型失败: {str(e)}")
        
        # 编码输入文本
        inputs = tokenizer(
            request.text,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )
        
        # 预测
        model.eval()
        with torch.no_grad():
            outputs = model(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'])
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = predictions[0][predicted_class].item()
        
        # 构建响应
        class_names = ["负面", "正面"]
        result = {
            "text": request.text,
            "predicted_class": class_names[predicted_class],
            "confidence": confidence
        }
        
        return APIResponse.success(
            message="预测成功",
            data=result
        )
    except ModelNotFoundException as e:
        logger.error(f"预测失败: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"预测失败: {str(e)}", exc_info=True)
        raise InternalServerException(message="预测失败")

@app.get("/dataset/preview/{dataset_id}")
async def preview_dataset(dataset_id: int, limit: int = 10):
    try:
        # 获取数据集信息
        with get_session() as session:
            ds = session.get(DatasetORM, dataset_id)
            if not ds:
                raise DatasetNotFoundException(f"数据集 ID {dataset_id} 不存在")
            
            # 读取CSV文件
            import pandas as pd
            try:
                df = pd.read_csv(ds.file_path)
                # 检查必要的列是否存在
                if 'text' not in df.columns or 'label' not in df.columns:
                    raise InvalidParamsException("数据集格式错误：缺少必要的列（text 和 label）")
                
                # 获取前N行数据
                preview_data = df.head(limit).to_dict('records')
                return APIResponse.success(
                    message="获取数据集预览成功",
                    data={
                        "preview": preview_data,
                        "total_rows": len(df),
                        "dataset_info": {
                            "id": ds.id,
                            "name": ds.name,
                            "created_at": ds.created_at.isoformat()
                        }
                    }
                )
            except Exception as e:
                logger.error(f"读取数据集文件失败：{str(e)}", exc_info=True)
                raise InternalServerException(message=f"读取数据集文件失败")
    except (DatasetNotFoundException, InvalidParamsException) as e:
        # 这些异常已经在上面抛出
        logger.error(f"获取数据集预览失败：{str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"获取数据集预览失败：{str(e)}", exc_info=True)
        raise InternalServerException(message="获取数据集预览失败")

# 训练函数，将在后台运行
async def train_model_task(job_id: int, dataset_id: int, epochs: int, learning_rate: float, batch_size: int):
    try:
        # 获取数据集信息
        with get_session() as session:
            dataset = session.get(DatasetORM, dataset_id)
            if not dataset:
                logger.error(f"数据集不存在: {dataset_id}")
                update_job_status(job_id, "failed", error_message="数据集不存在")
                return
            
            # 更新任务状态为运行中
            job = session.get(TrainingJobORM, job_id)
            job.status = "running"
            job.started_at = datetime.utcnow()
            session.add(job)
            session.commit()
        
        # 创建日志文件
        log_file = f"{LOG_PATH}/training_job_{job_id}_{int(datetime.now().timestamp())}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        job_logger = logging.getLogger(f"job_{job_id}")
        job_logger.addHandler(file_handler)
        job_logger.setLevel(logging.INFO)
        
        # 更新日志文件路径
        with get_session() as session:
            job = session.get(TrainingJobORM, job_id)
            job.log_file = log_file
            session.add(job)
            session.commit()
        
        # 加载数据集
        job_logger.info(f"加载数据集: {dataset.file_path}")
        df = pd.read_csv(dataset.file_path)
        
        # 检查数据集格式
        if 'text' not in df.columns or 'label' not in df.columns:
            error_msg = "数据集必须包含'text'和'label'列"
            job_logger.error(error_msg)
            update_job_status(job_id, "failed", error_message=error_msg)
            return
        
        # 准备数据
        texts = df['text'].tolist()
        labels = df['label'].tolist()
        
        # 初始化tokenizer和模型
        job_logger.info("初始化tokenizer和模型")
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=len(set(labels)))
        
        # 准备数据集
        class TextDataset(Dataset):
            def __init__(self, texts, labels, tokenizer, max_length=128):
                self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=max_length, return_tensors='pt')
                self.labels = torch.tensor(labels, dtype=torch.long)
            
            def __getitem__(self, idx):
                item = {key: val[idx] for key, val in self.encodings.items()}
                item['labels'] = self.labels[idx]
                return item
            
            def __len__(self):
                return len(self.labels)
        
        dataset = TextDataset(texts, labels, tokenizer)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # 设置优化器
        optimizer = AdamW(model.parameters(), lr=learning_rate)
        
        # 训练模型
        job_logger.info(f"开始训练，共{epochs}轮")
        total_steps = epochs * len(dataloader)
        current_step = 0
        
        for epoch in range(epochs):
            job_logger.info(f"开始第{epoch+1}轮训练")
            for batch in dataloader:
                # 检查任务是否被停止
                with get_session() as session:
                    job = session.get(TrainingJobORM, job_id)
                    if job.status == "stopped":
                        job_logger.info("训练任务已被手动停止")
                        return
                
                # 前向传播和反向传播
                optimizer.zero_grad()
                input_ids = batch['input_ids']
                attention_mask = batch['attention_mask']
                labels = batch['labels']
                
                outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                
                job_logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
                
                loss.backward()
                optimizer.step()
                
                # 更新进度
                current_step += 1
                progress = (current_step / total_steps) * 100
                
                # 每10步更新一次进度
                if current_step % 10 == 0 or current_step == total_steps:
                    with get_session() as session:
                        job = session.get(TrainingJobORM, job_id)
                        job.progress = progress
                        session.add(job)
                        session.commit()
        
        # 保存模型
        model_save_path = f"{MODEL_PATH}/model_{dataset_id}_{job_id}_{int(datetime.now().timestamp())}"
        job_logger.info(f"保存模型到: {model_save_path}")
        model.save_pretrained(model_save_path)
        tokenizer.save_pretrained(model_save_path)
        
        # 更新训练任务状态为成功
        update_job_status(job_id, "succeeded", model_path=model_save_path)
        job_logger.info("训练完成")
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"训练失败: {error_message}")
        update_job_status(job_id, "failed", error_message=error_message)

# 更新任务状态的辅助函数
def update_job_status(job_id: int, status: str, model_path: str = None, error_message: str = None):
    with get_session() as session:
        job = session.get(TrainingJobORM, job_id)
        if not job:
            logger.error(f"找不到训练任务: {job_id}")
            return
        
        job.status = status
        job.completed_at = datetime.utcnow()
        
        if model_path:
            job.model_name = model_path
        
        if status == "succeeded":
            job.progress = 100.0
        
        session.add(job)
        session.commit()
        
        # 记录错误信息到日志文件
        if error_message and job.log_file:
            with open(job.log_file, "a") as f:
                f.write(f"\n[ERROR] {datetime.now()} - {error_message}\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)


class PredictionRequest:
    def __init__(self, model_id: int, text: str):
        self.model_id = model_id
        self.text = text

# 数据集上传接口
@app.post("/api/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        # 检查文件类型
        if not file.filename.endswith('.csv'):
            return APIResponse.error("只支持CSV文件格式")
        
        # 保存文件
        file_path = f"{UPLOAD_PATH}/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 验证CSV格式
        try:
            df = pd.read_csv(file_path)
            if 'text' not in df.columns or 'label' not in df.columns:
                os.remove(file_path)  # 删除不符合要求的文件
                return APIResponse.error("CSV文件必须包含'text'和'label'列")
        except Exception as e:
            os.remove(file_path)  # 删除无法解析的文件
            return APIResponse.error(f"CSV文件解析失败: {str(e)}")
        
        # 保存到数据库
        with get_session() as session:
            dataset = DatasetORM(name=file.filename, file_path=file_path)
            session.add(dataset)
            session.commit()
            session.refresh(dataset)
        
        return APIResponse.success(
            {"id": dataset.id, "name": dataset.name, "file_path": dataset.file_path},
            "数据集上传成功"
        )
    except Exception as e:
        logger.error(f"数据集上传失败: {str(e)}")
        return APIResponse.error(f"数据集上传失败: {str(e)}")

# 获取数据集列表
@app.get("/api/datasets")
async def get_datasets():
    try:
        with get_session() as session:
            statement = select(DatasetORM)
            results = session.exec(statement).all()
            datasets = [
                {"id": ds.id, "name": ds.name, "file_path": ds.file_path, "created_at": ds.created_at}
                for ds in results
            ]
        return APIResponse.success(datasets, "获取数据集列表成功")
    except Exception as e:
        logger.error(f"获取数据集列表失败: {str(e)}")
        return APIResponse.error(f"获取数据集列表失败: {str(e)}")

# 获取数据集预览
@app.get("/api/datasets/{dataset_id}/preview")
async def preview_dataset(dataset_id: int, limit: int = Query(10, ge=1, le=100)):
    try:
        with get_session() as session:
            dataset = session.get(DatasetORM, dataset_id)
            if not dataset:
                return APIResponse.error("数据集不存在", 404)
            
            # 读取CSV文件并返回前N行
            df = pd.read_csv(dataset.file_path)
            preview_data = df.head(limit).to_dict(orient='records')
            
            return APIResponse.success({
                "dataset": {"id": dataset.id, "name": dataset.name},
                "preview": preview_data,
                "total_rows": len(df),
                "columns": df.columns.tolist()
            }, "获取数据集预览成功")
    except Exception as e:
        logger.error(f"获取数据集预览失败: {str(e)}")
        return APIResponse.error(f"获取数据集预览失败: {str(e)}")

# 启动训练接口
@app.post("/api/train/start")
async def start_training(request: dict, background_tasks: BackgroundTasks):
    try:
        # 解析请求参数
        training_request = TrainingRequest(
            dataset_id=request.get("dataset_id"),
            epochs=request.get("epochs", 3),
            learning_rate=request.get("learning_rate", 2e-5),
            batch_size=request.get("batch_size", 16)
        )
        
        # 验证数据集是否存在
        with get_session() as session:
            dataset = session.get(DatasetORM, training_request.dataset_id)
            if not dataset:
                return APIResponse.error("数据集不存在", 404)
            
            # 创建训练任务记录
            job = TrainingJobORM(
                dataset_id=training_request.dataset_id,
                status="pending",
                epochs=training_request.epochs,
                learning_rate=training_request.learning_rate,
                batch_size=training_request.batch_size,
                progress=0.0
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            
            # 启动后台训练任务
            background_tasks.add_task(
                train_model_task,
                job_id=job.id,
                dataset_id=training_request.dataset_id,
                epochs=training_request.epochs,
                learning_rate=training_request.learning_rate,
                batch_size=training_request.batch_size
            )
            
            return APIResponse.success(
                {"job_id": job.id, "status": job.status},
                "训练任务已提交"
            )
    except Exception as e:
        logger.error(f"启动训练失败: {str(e)}")
        return APIResponse.error(f"启动训练失败: {str(e)}")

# 获取训练状态
@app.get("/api/train/status/{job_id}")
async def get_training_status(job_id: int):
    try:
        with get_session() as session:
            job = session.get(TrainingJobORM, job_id)
            if not job:
                return APIResponse.error("训练任务不存在", 404)
            
            # 构建响应数据
            response_data = {
                "job_id": job.id,
                "dataset_id": job.dataset_id,
                "status": job.status,
                "progress": job.progress,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "model_name": job.model_name
            }
            
            # 如果有日志文件，读取最新的日志内容
            if job.log_file and os.path.exists(job.log_file):
                with open(job.log_file, "r") as f:
                    # 读取最后20行日志
                    log_lines = f.readlines()
                    response_data["logs"] = log_lines[-20:] if len(log_lines) > 20 else log_lines
            
            return APIResponse.success(response_data, "获取训练状态成功")
    except Exception as e:
        logger.error(f"获取训练状态失败: {str(e)}")
        return APIResponse.error(f"获取训练状态失败: {str(e)}")

# 停止训练
@app.post("/api/train/stop")
async def stop_training(request: dict):
    try:
        job_id = request.get("job_id")
        if not job_id:
            return APIResponse.error("缺少job_id参数")
        
        with get_session() as session:
            job = session.get(TrainingJobORM, job_id)
            if not job:
                return APIResponse.error("训练任务不存在", 404)
            
            # 只有处于pending或running状态的任务才能被停止
            if job.status not in ["pending", "running"]:
                return APIResponse.error(f"无法停止状态为{job.status}的任务")
            
            # 更新任务状态为stopped
            job.status = "stopped"
            job.completed_at = datetime.utcnow()
            session.add(job)
            session.commit()
            
            return APIResponse.success({"job_id": job.id, "status": job.status}, "训练任务已停止")
    except Exception as e:
        logger.error(f"停止训练失败: {str(e)}")
        return APIResponse.error(f"停止训练失败: {str(e)}")

# 获取训练日志
@app.get("/api/train/logs/{job_id}")
async def get_training_logs(job_id: int, lines: int = Query(50, ge=1, le=1000)):
    try:
        with get_session() as session:
            job = session.get(TrainingJobORM, job_id)
            if not job:
                return APIResponse.error("训练任务不存在", 404)
            
            if not job.log_file or not os.path.exists(job.log_file):
                return APIResponse.error("日志文件不存在", 404)
            
            # 读取指定行数的日志
            with open(job.log_file, "r") as f:
                log_content = f.readlines()
                # 返回最后N行
                logs = log_content[-lines:] if len(log_content) > lines else log_content
            
            return APIResponse.success({"logs": logs}, "获取训练日志成功")
    except Exception as e:
        logger.error(f"获取训练日志失败: {str(e)}")
        return APIResponse.error(f"获取训练日志失败: {str(e)}")

# 获取所有训练任务
@app.get("/api/train/jobs")
async def get_training_jobs():
    try:
        with get_session() as session:
            statement = select(TrainingJobORM).order_by(TrainingJobORM.id.desc())
            results = session.exec(statement).all()
            jobs = [
                {
                    "id": job.id,
                    "dataset_id": job.dataset_id,
                    "status": job.status,
                    "progress": job.progress,
                    "started_at": job.started_at,
                    "completed_at": job.completed_at,
                    "model_name": job.model_name
                }
                for job in results
            ]
            return APIResponse.success(jobs, "获取训练任务列表成功")
    except Exception as e:
        logger.error(f"获取训练任务列表失败: {str(e)}")
        return APIResponse.error(f"获取训练任务列表失败: {str(e)}")