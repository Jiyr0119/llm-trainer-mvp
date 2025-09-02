from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
import json
from typing import List, Optional
import torch
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
from torch.utils.data import DataLoader, Dataset
import pandas as pd
import shutil
from datetime import datetime

app = FastAPI(title="LLM Trainer MVP", description="MVP版本的大语言模型训练平台")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库初始化
DATABASE_PATH = "../data/database.db"
MODEL_PATH = "../data/models"

# 创建数据目录
os.makedirs(MODEL_PATH, exist_ok=True)

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 创建数据集表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建训练任务表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id INTEGER,
            status TEXT DEFAULT 'pending',
            model_name TEXT,
            epochs INTEGER DEFAULT 3,
            learning_rate REAL DEFAULT 2e-5,
            batch_size INTEGER DEFAULT 8,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (dataset_id) REFERENCES datasets (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

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
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)
    return model, tokenizer

# API路由
@app.get("/")
async def root():
    return {"message": "LLM Trainer MVP API"}

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        # 保存文件
        file_path = f"../data/uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 保存到数据库
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO datasets (name, file_path) VALUES (?, ?)",
            (file.filename, file_path)
        )
        dataset_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"id": dataset_id, "filename": file.filename, "message": "数据集上传成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets")
async def list_datasets():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, file_path, created_at FROM datasets")
    datasets = cursor.fetchall()
    conn.close()
    
    return [{"id": row[0], "name": row[1], "file_path": row[2], "created_at": row[3]} for row in datasets]

@app.post("/train", response_model=TrainingStatus)
async def start_training(request: TrainingRequest):
    try:
        # 获取数据集信息
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM datasets WHERE id = ?", (request.dataset_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="数据集未找到")
        
        file_path = result[0]
        
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
        
        # 更新训练任务状态
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO training_jobs (dataset_id, status, model_name, epochs, learning_rate, batch_size, started_at, completed_at) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            (request.dataset_id, 'completed', model_save_path, request.epochs, request.learning_rate, request.batch_size)
        )
        conn.commit()
        conn.close()
        
        return TrainingStatus(status="completed", message="训练完成")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/train/status")
async def get_training_status():
    # 简化实现，实际项目中应查询具体的训练任务状态
    return {"status": "ready", "message": "准备就绪"}

@app.post("/predict")
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
        
        return {
            "text": request.text,
            "predicted_class": predicted_class,
            "confidence": confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)