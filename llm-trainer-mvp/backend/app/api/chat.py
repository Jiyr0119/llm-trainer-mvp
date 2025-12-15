from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional, AsyncGenerator
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
import os
import json
import asyncio
import torch

from app.core.config import settings
from app.api.auth import get_current_active_user
from app.models import User
from app.core.decorators import standardized_response

# 创建路由器
router = APIRouter(prefix="/chat", tags=["chat"])

# 模型定义
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: int = 1024
    stream: bool = False

class ChatCompletionChoice(BaseModel):
    message: Message
    finish_reason: str = "stop"

class ChatCompletionResponse(BaseModel):
    id: str
    model: str
    choices: List[ChatCompletionChoice]
    created: int

class Conversation(BaseModel):
    id: str
    title: str
    model: str
    created_at: str
    updated_at: str

class ConversationCreate(BaseModel):
    title: str
    model: str

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    title: str
    model: str
    created_at: str
    updated_at: str
    messages: List[Message] = []

class ModelInfo(BaseModel):
    id: str
    name: str
    description: str
    max_tokens: int
    created_at: str

class ModelSettings(BaseModel):
    model: str
    settings: dict

# 模拟数据存储
STATIC_MODELS = [
    {
        "id": "qwen-1.5-0.5b",
        "name": "Qwen-1.5-0.5B-Chat",
        "description": "通义千问1.5 0.5B对话模型，适合轻量级对话应用",
        "max_tokens": 2048,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "qwen-7b-chat",
        "name": "Qwen-7B-Chat",
        "description": "通义千问7B对话模型，适合一般对话任务",
        "max_tokens": 2048,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "deepseek-7b-chat",
        "name": "DeepSeek-7B-Chat",
        "description": "DeepSeek 7B对话模型，适合代码和文本生成",
        "max_tokens": 4096,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "llama2-7b-chat",
        "name": "Llama2-7B-Chat",
        "description": "Meta的Llama2 7B对话模型，通用对话能力",
        "max_tokens": 2048,
        "created_at": datetime.now().isoformat()
    }
]

# 动态获取已下载的模型
def get_available_models():
    """获取可用的模型列表，包括静态模型和已下载的模型"""
    import os
    from app.core.config import settings
    
    # 获取已下载的模型
    downloaded_models = []
    model_dir = settings.MODEL_PATH
    
    if os.path.exists(model_dir):
        for model_folder in os.listdir(model_dir):
            model_path = os.path.join(model_dir, model_folder)
            if os.path.isdir(model_path):
                # 检查是否是有效的模型目录（包含config.json）
                config_path = os.path.join(model_path, "config.json")
                if os.path.exists(config_path):
                    downloaded_models.append({
                        "id": model_folder,
                        "name": model_folder,
                        "description": f"已下载的本地模型: {model_folder}",
                        "max_tokens": 2048,
                        "created_at": datetime.now().isoformat()
                    })
    
    # 合并静态模型和已下载的模型
    return downloaded_models + STATIC_MODELS

# 数据存储路径
CONVERSATIONS_DIR = os.path.join(settings.DATA_DIR, "conversations")
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

# 工具函数
def get_user_conversations_dir(user_id: int):
    user_dir = os.path.join(CONVERSATIONS_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def save_conversation(user_id: int, conversation_id: str, data: dict):
    user_dir = get_user_conversations_dir(user_id)
    file_path = os.path.join(user_dir, f"{conversation_id}.json")
    with open(file_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_conversation(user_id: int, conversation_id: str):
    user_dir = get_user_conversations_dir(user_id)
    file_path = os.path.join(user_dir, f"{conversation_id}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)

def list_conversations(user_id: int):
    user_dir = get_user_conversations_dir(user_id)
    conversations = []
    for filename in os.listdir(user_dir):
        if filename.endswith(".json"):
            with open(os.path.join(user_dir, filename), "r") as f:
                conv = json.load(f)
                # 只返回元数据，不包含消息
                conversations.append({
                    "id": conv["id"],
                    "title": conv["title"],
                    "model": conv["model"],
                    "created_at": conv["created_at"],
                    "updated_at": conv["updated_at"]
                })
    # 按更新时间倒序排序
    conversations.sort(key=lambda x: x["updated_at"], reverse=True)
    return conversations

def delete_conversation(user_id: int, conversation_id: str):
    user_dir = get_user_conversations_dir(user_id)
    file_path = os.path.join(user_dir, f"{conversation_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# 模型缓存
MODEL_CACHE = {}

# 模型路径
MODEL_DIR = settings.MODEL_PATH

# 加载模型
def load_model(model_id: str):
    if model_id in MODEL_CACHE:
        return MODEL_CACHE[model_id]
    
    model_path = os.path.join(MODEL_DIR, model_id)
    if not os.path.exists(model_path):
        # 如果模型不存在，返回None
        return None
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        MODEL_CACHE[model_id] = {"tokenizer": tokenizer, "model": model}
        return MODEL_CACHE[model_id]
    except Exception as e:
        print(f"加载模型{model_id}时出错: {str(e)}")
        return None

# 模型推理
def generate_response(model: str, messages: List[Message], temperature: float, max_tokens: int):
    # 尝试加载本地模型
    model_data = load_model(model)
    
    if model_data:
        # 使用本地模型生成回复
        try:
            tokenizer = model_data["tokenizer"]
            model_instance = model_data["model"]
            
            # 将消息格式化为模型输入
            if model.startswith("qwen"):
                # Qwen模型的输入格式
                prompt = ""
                for msg in messages:
                    if msg.role == "user":
                        prompt += f"<|im_start|>user\n{msg.content}<|im_end|>\n"
                    elif msg.role == "assistant":
                        prompt += f"<|im_start|>assistant\n{msg.content}<|im_end|>\n"
                    elif msg.role == "system":
                        prompt += f"<|im_start|>system\n{msg.content}<|im_end|>\n"
                prompt += "<|im_start|>assistant\n"
            else:
                # 默认格式
                prompt = ""
                for msg in messages:
                    prompt += f"{msg.role}: {msg.content}\n"
                prompt += "assistant: "
            
            # 生成回复
            inputs = tokenizer(prompt, return_tensors="pt").to(model_instance.device)
            outputs = model_instance.generate(
                inputs.input_ids,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id
            )
            
            # 解码回复
            response_text = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            
            return {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "model": model,
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response_text
                        },
                        "finish_reason": "stop"
                    }
                ],
                "created": int(datetime.now().timestamp())
            }
        except Exception as e:
            print(f"模型推理出错: {str(e)}")
            # 如果模型推理出错，回退到模拟实现
            pass

# 流式响应生成
async def generate_stream_response(model: str, messages: List[Message], temperature: float, max_tokens: int) -> AsyncGenerator[str, None]:
    # 生成唯一ID
    response_id = f"chatcmpl-{uuid.uuid4()}"
    created_time = int(datetime.now().timestamp())
    
    # 尝试加载本地模型
    model_data = load_model(model)
    
    if model_data:
        try:
            tokenizer = model_data["tokenizer"]
            model_instance = model_data["model"]
            
            # 将消息格式化为模型输入
            if model.startswith("qwen"):
                # Qwen模型的输入格式
                prompt = ""
                for msg in messages:
                    if msg.role == "user":
                        prompt += f"<|im_start|>user\n{msg.content}<|im_end|>\n"
                    elif msg.role == "assistant":
                        prompt += f"<|im_start|>assistant\n{msg.content}<|im_end|>\n"
                    elif msg.role == "system":
                        prompt += f"<|im_start|>system\n{msg.content}<|im_end|>\n"
                prompt += "<|im_start|>assistant\n"
            else:
                # 默认格式
                prompt = ""
                for msg in messages:
                    prompt += f"{msg.role}: {msg.content}\n"
                prompt += "assistant: "
            
            # 准备输入
            inputs = tokenizer(prompt, return_tensors="pt").to(model_instance.device)
            
            # 发送开始事件
            start_data = {
                "id": response_id,
                "model": model,
                "created": created_time,
                "choices": [{
                    "delta": {"role": "assistant"},
                    "index": 0
                }]
            }
            yield f"data: {json.dumps(start_data)}\n\n"
            
            # 使用流式生成
            generated_text = ""
            
            # 逐个token生成
            for i in range(max_tokens):
                with torch.no_grad():
                    if i == 0:
                        # 第一个token
                        outputs = model_instance.generate(
                            inputs.input_ids,
                            max_new_tokens=1,
                            temperature=temperature,
                            do_sample=temperature > 0,
                            pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
                            return_dict_in_generate=True,
                            output_scores=True
                        )
                        token = outputs.sequences[0][-1].unsqueeze(0)
                    else:
                        # 后续token
                        outputs = model_instance.generate(
                            torch.cat([inputs.input_ids, token], dim=1),
                            max_new_tokens=1,
                            temperature=temperature,
                            do_sample=temperature > 0,
                            pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
                            return_dict_in_generate=True,
                            output_scores=True
                        )
                        token = outputs.sequences[0][-1].unsqueeze(0)
                    
                    # 解码当前token
                    token_text = tokenizer.decode(token[0], skip_special_tokens=True)
                    
                    # 如果是结束标记或空白，结束生成
                    if token.item() == tokenizer.eos_token_id or not token_text.strip():
                        break
                    
                    # 累积生成的文本
                    generated_text += token_text
                    
                    # 发送当前token
                    token_data = {
                        "id": response_id,
                        "model": model,
                        "created": created_time,
                        "choices": [{
                            "delta": {"content": token_text},
                            "index": 0
                        }]
                    }
                    yield f"data: {json.dumps(token_data)}\n\n"
                    
                    # 添加短暂延迟，模拟真实打字效果
                    await asyncio.sleep(0.01)
            
            # 发送结束事件
            end_data = {
                "id": response_id,
                "model": model,
                "created": created_time,
                "choices": [{
                    "delta": {},
                    "finish_reason": "stop",
                    "index": 0
                }]
            }
            yield f"data: {json.dumps(end_data)}\n\n"
            yield "data: [DONE]\n\n"
            return
        except Exception as e:
            print(f"流式模型推理出错: {str(e)}")
            # 如果出错，回退到模拟实现
    
    # 模拟实现（当本地模型不可用或推理出错时使用）
    last_message = messages[-1].content if messages else ""
    
    if "python" in last_message.lower():
        response = "```python\ndef hello_world():\n    print('Hello, World!')\n\nhello_world()\n```\n\n这是一个简单的Python函数，它会打印'Hello, World!'。"
    elif "代码" in last_message or "code" in last_message.lower():
        response = "以下是一个简单的JavaScript函数示例：\n\n```javascript\nfunction calculateSum(a, b) {\n    return a + b;\n}\n\nconst result = calculateSum(5, 3);\nconsole.log(result); // 输出: 8\n```\n\n这个函数接受两个参数并返回它们的和。"
    else:
        response = f"这是来自{model}模型的回复。您的问题是关于'{last_message[:30]}...'。在实际实现中，这里会返回真实模型的推理结果。"
    
    # 发送开始事件
    start_data = {
        "id": response_id,
        "model": model,
        "created": created_time,
        "choices": [{
            "delta": {"role": "assistant"},
            "index": 0
        }]
    }
    yield f"data: {json.dumps(start_data)}\n\n"
    
    # 模拟流式输出，每次发送一个字符
    for i, char in enumerate(response):
        char_data = {
            "id": response_id,
            "model": model,
            "created": created_time,
            "choices": [{
                "delta": {"content": char},
                "index": 0
            }]
        }
        yield f"data: {json.dumps(char_data)}\n\n"
        await asyncio.sleep(0.01)  # 模拟打字延迟
    
    # 发送结束事件
    end_data = {
        "id": response_id,
        "model": model,
        "created": created_time,
        "choices": [{
            "delta": {},
            "finish_reason": "stop",
            "index": 0
        }]
    }
    yield f"data: {json.dumps(end_data)}\n\n"
    yield "data: [DONE]\n\n"

# API路由
@router.get("/models", response_model=dict)
@standardized_response("获取模型列表成功")
async def get_models(current_user: User = Depends(get_current_active_user)):
    """获取可用的语言模型列表"""
    return {"models": get_available_models()}

@router.get("/conversations", response_model=dict)
@standardized_response("获取对话列表成功")
async def get_conversations(current_user: User = Depends(get_current_active_user)):
    """获取用户的对话列表"""
    conversations = list_conversations(current_user.id if current_user.id is not None else 0)
    return {"conversations": conversations}

@router.post("/conversations", response_model=Conversation)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_active_user)
):
    """创建新的对话"""
    now = datetime.now().isoformat()
    conversation_id = str(uuid.uuid4())
    
    new_conversation = {
        "id": conversation_id,
        "title": conversation.title,
        "model": conversation.model,
        "created_at": now,
        "updated_at": now,
        "messages": []
    }
    
    save_conversation(current_user.id if current_user.id is not None else 0, conversation_id, new_conversation)
    
    return {
        "id": conversation_id,
        "title": conversation.title,
        "model": conversation.model,
        "created_at": now,
        "updated_at": now
    }

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """获取特定对话的详细信息"""
    conversation = load_conversation(current_user.id if current_user.id is not None else 0, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation

@router.patch("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新对话信息"""
    conversation = load_conversation(current_user.id if current_user.id is not None else 0, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if update_data.title is not None:
        conversation["title"] = update_data.title
    
    conversation["updated_at"] = datetime.now().isoformat()
    save_conversation(current_user.id if current_user.id is not None else 0, conversation_id, conversation)
    
    return {
        "id": conversation["id"],
        "title": conversation["title"],
        "model": conversation["model"],
        "created_at": conversation["created_at"],
        "updated_at": conversation["updated_at"]
    }

@router.delete("/conversations/{conversation_id}", response_model=dict)
async def delete_conversation_endpoint(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """删除对话"""
    success = delete_conversation(current_user.id if current_user.id is not None else 0, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"status": "success", "message": "Conversation deleted"}

@router.post("/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """创建聊天完成"""
    # 验证模型是否存在
    available_models = get_available_models()
    model_exists = any(m["id"] == request.model for m in available_models)
    if not model_exists:
        raise HTTPException(status_code=400, detail=f"Model {request.model} not found")
    
    # 如果不是流式输出，直接生成回复
    if not request.stream:
        response = generate_response(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return response
    else:
        # 流式输出使用StreamingResponse
        return StreamingResponse(
            generate_stream_response(
                model=request.model,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ),
            media_type="text/event-stream"
        )

@router.patch("/models/settings", response_model=dict)
async def update_model_settings(
    settings_data: ModelSettings,
    current_user: User = Depends(get_current_active_user)
):
    """更新模型设置"""
    # 这里是模拟实现，实际项目中应该保存用户的模型设置
    return {
        "status": "success",
        "message": "Settings updated",
        "model": settings_data.model,
        "settings": settings_data.settings
    }