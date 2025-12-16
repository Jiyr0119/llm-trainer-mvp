from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional, AsyncGenerator
from pydantic import BaseModel
import uuid
from datetime import datetime
import os
import json
import asyncio
import logging

from app.core.config import settings
from app.api.auth import get_current_active_user
from app.models import User
from app.core.decorators import standardized_response

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/chat", tags=["chat"])

# ==================== Models ====================
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False

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

# ==================== Static Data ====================
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

# ==================== Storage ====================
CONVERSATIONS_DIR = os.path.join(settings.DATA_DIR, "conversations")
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

def get_user_conversations_dir(user_id: int) -> str:
    """获取用户的对话目录"""
    user_dir = os.path.join(CONVERSATIONS_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def save_conversation(user_id: int, conversation_id: str, data: dict):
    """保存对话数据"""
    try:
        user_dir = get_user_conversations_dir(user_id)
        file_path = os.path.join(user_dir, f"{conversation_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved conversation {conversation_id} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to save conversation: {e}")
        raise

def load_conversation(user_id: int, conversation_id: str) -> Optional[dict]:
    """加载对话数据"""
    try:
        user_dir = get_user_conversations_dir(user_id)
        file_path = os.path.join(user_dir, f"{conversation_id}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load conversation: {e}")
        return None

def list_conversations(user_id: int) -> List[dict]:
    """列出用户的所有对话"""
    try:
        user_dir = get_user_conversations_dir(user_id)
        conversations = []
        for filename in os.listdir(user_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(user_dir, filename), "r", encoding="utf-8") as f:
                        conv = json.load(f)
                        conversations.append({
                            "id": conv["id"],
                            "title": conv["title"],
                            "model": conv["model"],
                            "created_at": conv["created_at"],
                            "updated_at": conv["updated_at"]
                        })
                except:
                    continue
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        return conversations
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        return []

def delete_conversation(user_id: int, conversation_id: str) -> bool:
    """删除对话"""
    try:
        user_dir = get_user_conversations_dir(user_id)
        file_path = os.path.join(user_dir, f"{conversation_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        return False

# ==================== Mock Response Generator ====================
async def generate_mock_stream_response(
    model: str, 
    messages: List[Message], 
    temperature: float, 
    max_tokens: int
) -> AsyncGenerator[str, None]:
    """生成模拟流式响应(当本地模型不可用时使用)"""
    response_id = f"chatcmpl-{uuid.uuid4()}"
    created_time = int(datetime.now().timestamp())
    
    # 根据用户输入生成响应
    last_message = messages[-1].content if messages else ""
    
    if "python" in last_message.lower():
        response = """Sure! Here's a simple Python example:

```python
def greet(name):
    return f"Hello, {name}!"

# Test the function
result = greet("World")
print(result)  # Output: Hello, World!
```

This function takes a name as input and returns a greeting message."""
    elif "代码" in last_message or "code" in last_message.lower():
        response = """Here's a JavaScript example:

```javascript
function calculateSum(a, b) {
    return a + b;
}

const result = calculateSum(5, 3);
console.log(result); // Output: 8
```

This function adds two numbers and returns the sum."""
    else:
        response = f"Thank you for your question about '{last_message[:50]}...'. This is a simulated response from the {model} model. In a production environment, this would be replaced with actual AI model inference."
    
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
    yield f"data: {json.dumps(start_data, ensure_ascii=False)}\n\n"
    
    # 模拟流式输出
    for char in response:
        char_data = {
            "id": response_id,
            "model": model,
            "created": created_time,
            "choices": [{
                "delta": {"content": char},
                "index": 0
            }]
        }
        yield f"data: {json.dumps(char_data, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.015)  # 模拟打字延迟
    
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
    yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"

# ==================== API Routes ====================
@router.get("/models", response_model=dict)
@standardized_response("获取模型列表成功")
async def get_models(current_user: User = Depends(get_current_active_user)):
    """获取可用的语言模型列表"""
    return {"models": STATIC_MODELS}

@router.get("/conversations", response_model=dict)
@standardized_response("获取对话列表成功")
async def get_conversations(current_user: User = Depends(get_current_active_user)):
    """获取用户的对话列表"""
    user_id = current_user.id if current_user.id is not None else 0
    conversations = list_conversations(user_id)
    return {"conversations": conversations}

@router.post("/conversations", response_model=Conversation)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_active_user)
):
    """创建新的对话"""
    now = datetime.now().isoformat()
    conversation_id = str(uuid.uuid4())
    user_id = current_user.id if current_user.id is not None else 0
    
    new_conversation = {
        "id": conversation_id,
        "title": conversation.title,
        "model": conversation.model,
        "created_at": now,
        "updated_at": now,
        "messages": []
    }
    
    save_conversation(user_id, conversation_id, new_conversation)
    
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
    user_id = current_user.id if current_user.id is not None else 0
    conversation = load_conversation(user_id, conversation_id)
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
    user_id = current_user.id if current_user.id is not None else 0
    conversation = load_conversation(user_id, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if update_data.title is not None:
        conversation["title"] = update_data.title
    
    conversation["updated_at"] = datetime.now().isoformat()
    save_conversation(user_id, conversation_id, conversation)
    
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
    user_id = current_user.id if current_user.id is not None else 0
    success = delete_conversation(user_id, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"status": "success", "message": "Conversation deleted"}

@router.post("/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """创建聊天完成(支持流式输出)"""
    logger.info(f"Chat completion request: model={request.model}, stream={request.stream}, messages={len(request.messages)}")
    
    # 验证模型是否存在
    model_exists = any(m["id"] == request.model for m in STATIC_MODELS)
    if not model_exists:
        raise HTTPException(status_code=400, detail=f"Model {request.model} not found")
    
    # 流式输出
    if request.stream:
        return StreamingResponse(
            generate_mock_stream_response(
                model=request.model,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        # 非流式输出 (简化实现)
        raise HTTPException(status_code=400, detail="Non-streaming mode not implemented. Please use stream=true")

@router.patch("/models/settings", response_model=dict)
async def update_model_settings(
    current_user: User = Depends(get_current_active_user)
):
    """更新模型设置"""
    return {
        "status": "success",
        "message": "Settings updated"
    }