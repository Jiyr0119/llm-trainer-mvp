from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from typing import List, Optional, Dict, Any, Union
import torch
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
from torch.utils.data import DataLoader, Dataset
import pandas as pd
import shutil
from datetime import datetime

from app.db import init_db, get_session
from app.models import Dataset as DatasetORM, TrainingJob as TrainingJobORM
from sqlmodel import select, desc

app = FastAPI(title="LLM Trainer MVP", description="MVP版本的大语言模型训练平台")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路径与目录
MODEL_PATH = "../data/models"
# 创建数据目录
os.makedirs(MODEL_PATH, exist_ok=True)

# 初始化数据库（ORM）
init_db()

# 统一API响应格式
class APIResponse(BaseModel):
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

# 数据模型
class DatasetInfo(BaseModel):
    name: str
    file_path: str

class TrainingRequest(BaseModel):
    dataset_id: int
    epochs: int = 3
    learning_rate: float = 2e-5
    batch_size: int = 8

class PredictionRequest(BaseModel):
    text: str

class TrainingStatus(BaseModel):
    status: str
    message: str
    job_id: Optional[int] = None

# 自定义数据集类
class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# 加载模型和分词器
def load_model_and_tokenizer():
    model_name = 'bert-base-chinese'
    try:
        # 尝试从本地加载模型
        local_model_path = os.path.join(MODEL_PATH, model_name)
        if os.path.exists(local_model_path):
            print(f"从本地加载模型: {local_model_path}")
            tokenizer = BertTokenizer.from_pretrained(local_model_path)
            model = BertForSequenceClassification.from_pretrained(local_model_path, num_labels=2)
        else:
            # 从Hugging Face下载模型
            print(f"从Hugging Face下载模型: {model_name}")
            tokenizer = BertTokenizer.from_pretrained(model_name)
            model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)
            
            # 保存到本地
            os.makedirs(local_model_path, exist_ok=True)
            tokenizer.save_pretrained(local_model_path)
            model.save_pretrained(local_model_path)
            print(f"模型已保存到本地: {local_model_path}")
            
        return model, tokenizer
    except Exception as e:
        print(f"加载模型失败: {str(e)}")
        raise Exception(f"无法加载 '{model_name}' 的分词器。如果您尝试从 `https://huggingface.co/models` 加载，请确保本地不存在同名目录。否则，请确认 '{model_name}' 是正确的路径，且该目录包含 BertTokenizer 分词器所需的所有相关文件。")

# API路由
@app.get("/", response_model=APIResponse)
async def root():
    return APIResponse(code=200, message="成功", data={"message": "LLM Trainer MVP API"})

@app.post("/upload", response_model=APIResponse)
async def upload_dataset(file: UploadFile = File(...)):
    try:
        # 保存文件
        file_path = f"../data/uploads/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 保存到数据库（ORM）
        with get_session() as session:
            ds = DatasetORM(name=file.filename, file_path=file_path)
            session.add(ds)
            session.flush()  # 获取自增ID
            dataset_id = ds.id
        
        return APIResponse(
            code=200,
            message="数据集上传成功",
            data={
                "id": dataset_id,
                "filename": file.filename
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets", response_model=APIResponse)
async def list_datasets():
    with get_session() as session:
        results = session.exec(select(DatasetORM)).all()
        datasets = [
            {"id": d.id, "name": d.name, "file_path": d.file_path, "created_at": d.created_at.isoformat()}
            for d in results
        ]
        return APIResponse(
            code=200,
            message="获取数据集列表成功",
            data={"datasets": datasets}
        )

@app.post("/train", response_model=APIResponse)
async def start_training(request: TrainingRequest):
    try:
        # 获取数据集信息
        with get_session() as session:
            ds = session.get(DatasetORM, request.dataset_id)
            if not ds:
                raise HTTPException(status_code=404, detail="数据集未找到")
            file_path = ds.file_path
        
        # 读取数据
        df = pd.read_csv(file_path)
        texts = df['text'].tolist()
        labels = df['label'].tolist()
        
        # 加载模型和分词器
        model, tokenizer = load_model_and_tokenizer()
        
        # 创建数据集和数据加载器
        dataset = TextDataset(texts, labels, tokenizer)
        dataloader = DataLoader(dataset, batch_size=request.batch_size, shuffle=True)
        
        # 设置优化器
        optimizer = AdamW(model.parameters(), lr=request.learning_rate)
        
        # 训练模型
        model.train()
        for epoch in range(request.epochs):
            for batch in dataloader:
                optimizer.zero_grad()
                outputs = model(
                    input_ids=batch['input_ids'],
                    attention_mask=batch['attention_mask'],
                    labels=batch['labels']
                )
                loss = outputs.loss
                loss.backward()
                optimizer.step()
        
        # 保存模型
        model_save_path = f"{MODEL_PATH}/model_{request.dataset_id}_{int(datetime.now().timestamp())}"
        model.save_pretrained(model_save_path)
        tokenizer.save_pretrained(model_save_path)
        
        # 更新训练任务（ORM）
        with get_session() as session:
            job = TrainingJobORM(
                dataset_id=request.dataset_id,
                status='completed',
                model_name=model_save_path,
                epochs=request.epochs,
                learning_rate=request.learning_rate,
                batch_size=request.batch_size,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            session.add(job)
            session.flush()  # 获取自增ID
            job_id = job.id
        
        return APIResponse(
            code=200,
            message="训练完成",
            data={
                "status": "completed",
                "job_id": job_id
            }
        )
    except Exception as e:
        error_message = str(e)
        return APIResponse(
            code=500,
            message=f"训练失败: {error_message}",
            data=None
        )

@app.get("/train/status", response_model=APIResponse)
async def get_training_status():
    try:
        with get_session() as session:
            # 获取最近的训练任务
            job = session.exec(select(TrainingJobORM).order_by(desc(TrainingJobORM.id)).limit(1)).first()
            
            if not job:
                return APIResponse(
                    code=200,
                    message="没有训练记录",
                    data={"status": "ready", "job_id": None}
                )
            
            return APIResponse(
                code=200,
                message=f"训练状态: {job.status}",
                data={
                    "status": job.status,
                    "job_id": job.id
                }
            )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取训练状态失败: {str(e)}",
            data=None
        )

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

@app.post("/predict", response_model=APIResponse)
async def predict(request: PredictionRequest):
    try:
        # 加载最新的模型和分词器（简化实现）
        model, tokenizer = load_model_and_tokenizer()
        
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
        
        return APIResponse(
            code=200,
            message="预测成功",
            data={
                "text": request.text,
                "predicted_class": predicted_class,
                "confidence": confidence
            }
        )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"预测失败: {str(e)}",
            data=None
        )

@app.get("/dataset/preview/{dataset_id}", response_model=APIResponse)
async def preview_dataset(dataset_id: int, limit: int = 10):
    try:
        # 获取数据集信息
        with get_session() as session:
            ds = session.get(DatasetORM, dataset_id)
            if not ds:
                return APIResponse(
                    code=404,
                    message=f"数据集 ID {dataset_id} 不存在",
                    data=None
                )
            
            # 读取CSV文件
            import pandas as pd
            try:
                df = pd.read_csv(ds.file_path)
                # 检查必要的列是否存在
                if 'text' not in df.columns or 'label' not in df.columns:
                    return APIResponse(
                        code=400,
                        message="数据集格式错误：缺少必要的列（text 和 label）",
                        data=None
                    )
                
                # 获取前N行数据
                preview_data = df.head(limit).to_dict('records')
                return APIResponse(
                    code=200,
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
                return APIResponse(
                    code=500,
                    message=f"读取数据集文件失败：{str(e)}",
                    data=None
                )
    except Exception as e:
        return APIResponse(
            code=500,
            message=f"获取数据集预览失败：{str(e)}",
            data=None
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)